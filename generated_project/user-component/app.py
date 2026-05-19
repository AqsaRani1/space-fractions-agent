app.py
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Load environment variables
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_EXPIRE_DAYS = int(os.getenv('JWT_EXPIRE_DAYS'))

# Connect to PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200

# User registration
@app.route('/api/auth/register', methods=['POST'])
def register():
    # Validate input
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    username = data['username']
    password = data['password']

    # Check if user already exists
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if user:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409

    # Hash password and save to database
    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/api/auth/login', methods=['POST'])
def login():
    # Validate input
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    username = data['username']
    password = data['password']

    # Fetch user from database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    conn.close()

    if not user or not check_password_hash(user[2], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate JWT token
    payload = {
        'user_id': user[0],
        'username': user[1],
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    return jsonify({'token': token.decode('utf-8')}), 200

# Verify JWT token
@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    # Get token from headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401

    try:
        # Verify and decode the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        username = payload['username']

        # Return user information
        return jsonify({'user_id': user_id, 'username': username}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(debug=True)
```