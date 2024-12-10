import base64
import os
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import sqlite3
import io
from functools import wraps
from cryptography.fernet import Fernet
from dotenv import load_dotenv

test_key = 'PgFSiBrcHK65U9g1I-dSBZogQVGwqWjEL8l-HMlVLTw='
test_cipher = Fernet(test_key)

# ##testing decryption with wrong ket
# def decrypt_data(data):
#     """Decrypt data using a test key."""
#     try:
#         return test_cipher.decrypt(data)
#     except Exception as e:
#         print(f"Decryption failed: {e}")
#         raise e

# Load environment variables from .env file
load_dotenv(dotenv_path='key.env')

# Retrieve the encryption key from the environment variable
encryption_key = os.getenv('ENCRYPTION_KEY')

# Ensure the encryption key is a valid Fernet key
if not encryption_key:
    raise ValueError("ENCRYPTION_KEY not found in the .env file.")

# Convert the key to a bytes object (Fernet requires a byte key)
key = encryption_key.encode()
cipher = Fernet(key)

app = Flask(__name__)

##port blocking
BLOCKED_IPS = {'127.0.0.2'}  # Add IPs you want to block

def check_ip(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.remote_addr in BLOCKED_IPS:
            return jsonify({'error': 'blocked'}), 403
        return f(*args, **kwargs)
    return wrapper

# Set up the SQLite database
def get_db_connection():
    print("Connecting to the database...")
    conn = sqlite3.connect('artworks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    print("Initializing the database...")  # Debug print statement
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
    print("Database initialized successfully.")

init_db()

# Function to decode base64 image data
def decode_base64(image_data):
    """Decode a base64 string, add padding if necessary, and return binary data."""
    padding_needed = len(image_data) % 4
    if padding_needed != 0:
        image_data += '=' * (4 - padding_needed)  # Add padding to make the length a multiple of 4
    return base64.b64decode(image_data)

# Function to encrypt data
def encrypt_data(data):
    """Encrypt data using Fernet."""
    return cipher.encrypt(data)

# Function to decrypt data
def decrypt_data(data):
    """Decrypt data using Fernet."""
    return cipher.decrypt(data)
    # return test_cipher.decrypt(data)

# Home page (drawing page)
@app.route('/')
def index():
    print("GET / - Rendering the drawing page.")
    return render_template('index.html')

# Gallery page to view saved artworks
@app.route('/gallery')
@check_ip
def gallery():
    print("GET /gallery - Fetching all artworks from the database.")
    conn = get_db_connection()
    artworks = conn.execute('SELECT * FROM artworks').fetchall()
    print(f"Fetched {len(artworks)} artworks from the database.")
    # Add the data URL prefix when sending to template
    processed_artworks = []
    for artwork in artworks:
        artwork_dict = dict(artwork)
        # Decrypt the image data before displaying it
        decrypted_image = decrypt_data(artwork['image'])
        artwork_dict['image'] = f"data:image/png;base64,{base64.b64encode(decrypted_image).decode()}"
        processed_artworks.append(artwork_dict)
    conn.close()
    return render_template('gallery.html', artworks=processed_artworks)



# Delete an artwork
@app.route('/delete/<art_id>', methods=['POST'])
def delete_art(art_id):
    print(f"POST /delete/{art_id} - Deleting artwork with ID: {art_id}")
    conn = get_db_connection()
    conn.execute('DELETE FROM artworks WHERE id = ?', (art_id,))
    conn.commit()
    conn.close()
    print(f"Artwork with ID {art_id} deleted successfully.")
    return redirect(url_for('gallery'))



# Save art to database
@app.route('/save_art', methods=['POST'])
def save_art():
    title = request.form['title']
    description = request.form['description']
    image_data = request.form['image_data']

    print(f"POST /save_art - Received title: {title}, description: {description}")  # Debug print statement

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

    # Encrypt the image data before storing it
    encrypted_image_data = encrypt_data(image_data)

    # Store the encrypted binary image in the database
    try:
        conn = get_db_connection()
        print(f"Inserting artwork into database: Title={title}, Description={description}")
        conn.execute('''
            INSERT INTO artworks (title, description, image) 
            VALUES (?, ?, ?)
        ''', (title, description, encrypted_image_data))
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
    print(f"GET /export/{art_id} - Exporting artwork with ID: {art_id}")
    conn = get_db_connection()
    artwork = conn.execute('SELECT * FROM artworks WHERE id = ?', (art_id,)).fetchone()
    conn.close()

    if artwork:
        encrypted_image_data = artwork['image']
        try:
            # Decrypt the image data
            image_data = decrypt_data(encrypted_image_data)
        except Exception as e:
            print(f"Error decrypting image data: {e}")
            return "Error decrypting image data", 500

        # Check if the data starts with the PNG signature (for binary data)
        if image_data[:8] != b'\x89PNG\r\n\x1a\n':
            print("Invalid PNG image data detected.")
            return "Invalid PNG image data", 400

        # Send the image as a file
        print(f"Sending artwork with ID {art_id} as a PNG file.")
        return send_file(io.BytesIO(image_data), mimetype='image/png', as_attachment=True,
                         download_name=f"art_{art_id}.png")
    else:
        print(f"Artwork with ID {art_id} not found.")
        return "Artwork not found", 404

if __name__ == '__main__':
    app.run(debug=True)
