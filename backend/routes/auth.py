from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.database.connection import get_db_connection, hash_password, verify_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "User with this email already exists."}), 400
        
    hashed_pwd = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_pwd)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Auto-login after registration
        access_token = create_access_token(identity=str(user_id))
        return jsonify({
            "message": "User registered successfully.",
            "token": access_token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(user['password'], password):
        return jsonify({"message": "Invalid email or password."}), 401
        
    access_token = create_access_token(identity=str(user['id']))
    return jsonify({
        "message": "Logged in successfully.",
        "token": access_token,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email']
        }
    }), 200
