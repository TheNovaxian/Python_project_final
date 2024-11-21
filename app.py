from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
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


# Home page (drawing page)
@app.route('/')
def index():
    return render_template('index.html')


# Gallery page to view saved artworks
@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    artworks = conn.execute('SELECT * FROM artworks').fetchall()
    conn.close()
    return render_template('gallery.html', artworks=artworks)


# Save art to database
@app.route('/save_art', methods=['POST'])
def save_art():
    title = request.form['title']
    description = request.form['description']
    image_data = request.form['image_data']  # Image as base64 or similar

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO artworks (title, description, image) 
        VALUES (?, ?, ?)
    ''', (title, description, image_data))
    conn.commit()
    conn.close()

    return redirect(url_for('gallery'))


# Export art as PNG
@app.route('/export/<art_id>', methods=['GET'])
def export_art(art_id):
    conn = get_db_connection()
    artwork = conn.execute('SELECT * FROM artworks WHERE id = ?', (art_id,)).fetchone()
    conn.close()

    image_data = artwork['image']
    return send_file(io.BytesIO(image_data), mimetype='image/png', as_attachment=True,
                     download_name=f"art_{art_id}.png")


if __name__ == '__main__':
    app.run(debug=True)
