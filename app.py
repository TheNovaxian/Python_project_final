import base64
from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import io

app = Flask(__name__)

# Set up the SQLite database
def get_db_connection():
    conn = sqlite3.connect('artworks.db')
    conn.row_factory = sqlite3.Row
    return conn


# Initialize the database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS artworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            image BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# Function to decode base64 image data
def decode_base64(image_data):
    """Decode a base64 string, add padding if necessary, and return binary data."""
    padding_needed = len(image_data) % 4
    if padding_needed != 0:
        image_data += '=' * (4 - padding_needed)  # Add padding to make the length a multiple of 4
    return base64.b64decode(image_data)

# Home page (drawing page)
@app.route('/')
def index():
    return render_template('index.html')


# Gallery page to view saved artworks
@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    artworks = conn.execute('SELECT * FROM artworks').fetchall()
    # Add the data URL prefix when sending to template
    processed_artworks = []
    for artwork in artworks:
        artwork_dict = dict(artwork)
        artwork_dict['image'] = f"data:image/png;base64,{base64.b64encode(artwork['image']).decode()}"
        processed_artworks.append(artwork_dict)
    conn.close()
    return render_template('gallery.html', artworks=processed_artworks)

# Delete an artwork
@app.route('/delete/<art_id>', methods=['POST'])
def delete_art(art_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM artworks WHERE id = ?', (art_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gallery'))


# Save art to database
@app.route('/save_art', methods=['POST'])
def save_art():
    title = request.form['title']
    description = request.form['description']
    image_data = request.form['image_data']

    print(f"Received Title: {title}")
    print(f"Received Description: {description}")

    # Check if the image data starts with 'data:image/png;base64,' and decode it
    if image_data.startswith('data:image/png;base64,'):
        image_data = image_data.replace('data:image/png;base64,', '')  # Remove the base64 prefix
        print(f"Stripped image data (first 100 characters): {image_data[:100]}...")

        try:
            image_data = decode_base64(image_data)  # Decode to binary data
            print(f"Decoded image data length: {len(image_data)} bytes")
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
            return "Error decoding base64 image data", 400
    else:
        print("Invalid image data format received.")
        return "Invalid image data format", 400

    # Store the binary image in the database
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO artworks (title, description, image) 
            VALUES (?, ?, ?)
        ''', (title, description, image_data))
        conn.commit()
        conn.close()
        print(f"Artwork '{title}' saved successfully.")
    except Exception as e:
        print(f"Error saving artwork to the database: {e}")
        return f"Error saving artwork: {e}", 500

    return redirect(url_for('gallery'))


# Export art as PNG
@app.route('/export/<art_id>', methods=['GET'])
def export_art(art_id):
    conn = get_db_connection()
    artwork = conn.execute('SELECT * FROM artworks WHERE id = ?', (art_id,)).fetchone()
    conn.close()

    if artwork:
        image_data = artwork['image']

        # Check if the data starts with the PNG signature (for binary data)
        if image_data[:8] != b'\x89PNG\r\n\x1a\n':
            return "Invalid PNG image data", 400

        # Send the image as a file
        return send_file(io.BytesIO(image_data), mimetype='image/png', as_attachment=True,
                         download_name=f"art_{art_id}.png")
    else:
        return "Artwork not found", 404


if __name__ == '__main__':
    app.run(debug=True)
