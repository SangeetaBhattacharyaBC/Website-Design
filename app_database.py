# Importing required modules
from flask import Flask, jsonify, request   # Flask for web server, jsonify for returning JSON, request to handle user input
from flask_cors import CORS                 # Allows frontend (HTML/JS) to talk to backend securely
import sqlite3                              # SQLite is a lightweight database stored in a single file
from datetime import datetime               # To add timestamps to messages


# Initialise the Flask app
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows frontend files (HTML/JS) hosted elsewhere to access this backend API
CORS(app)


# Define the database file name
DATABASE = 'guestbook.db'


# 🧱 1. Function to connect to the database
def get_db_connection():
    # Connect to the SQLite database (creates it if not existing)
    conn = sqlite3.connect(DATABASE)
    # Allows us to access data using column names instead of just indexes
    conn.row_factory = sqlite3.Row
    return conn


# 🧩 2. Function to create the table (run once)
def create_table():
    # Connect to the database
    conn = get_db_connection()
    # Create the 'entries' table if it doesn’t already exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique ID for each entry
            name TEXT,                             -- name of the person
            message TEXT NOT NULL,                 -- their message (required)
            createdAt TEXT NOT NULL                -- time the entry was added
        )
    ''')
    conn.commit()   # Save changes
    conn.close()    # Close the connection


# 📜 3. Route to get all guestbook entries
@app.route('/api/entries', methods=['GET'])
def get_entries():
    # Connect to the database
    conn = get_db_connection()
    # Retrieve all rows from the entries table, newest first
    rows = conn.execute('SELECT * FROM entries ORDER BY id DESC').fetchall()
    conn.close()

    # Convert each row (SQLite Row object) into a Python dictionary
    entries = [dict(row) for row in rows]

    # Return all entries as JSON (so frontend can display them easily)
    return jsonify(entries)


# ✏️ 4. Route to add a new entry
@app.route('/api/entries', methods=['POST'])
def add_entry():
    # Get the data sent by the frontend (in JSON format)
    data = request.get_json()

    # Get the name and message from the data; default name is 'Anonymous'
    name = data.get('name', 'Anonymous').strip()
    message = data.get('message', '').strip()

    # If the message is empty, return an error (HTTP 400 = Bad Request)
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Get the current date and time in ISO format (e.g. 2025-11-03T12:34:56)
    createdAt = datetime.now().isoformat()

    # Insert the new entry into the database
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO entries (name, message, createdAt) VALUES (?, ?, ?)',
        (name, message, createdAt)
    )
    conn.commit()   # Save the new entry
    conn.close()    # Close the database connection

    # Return the new entry as JSON with status code 201 (Created)
    return jsonify({'name': name, 'message': message, 'createdAt': createdAt}), 201


# 🏠 5. Home route (for testing)
@app.route('/')
def home():
    # This is a simple message shown when someone opens the base URL
    return "✅ Guestbook Flask API is running. Use /api/entries to fetch or post data."


# 🚀 6. Run the app
if __name__ == '__main__':
    # Ensure the database table exists before starting the app
    create_table()

    # Start the Flask development server
    app.run(debug=True, port=5000)
