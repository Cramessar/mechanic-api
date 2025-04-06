# File: application/utils.py

from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import Customer, Mechanic
from config import Config

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"


def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

def encode_token(user_id, role="customer"):
    payload = {
        "sub": str(user_id),  
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"message": "Missing token!"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # remove after testing 
            print("🧠 Decoded Token Payload (Customer):", data)

            if data.get("role") != "customer":
                return jsonify({"message": "Unauthorized role!"}), 403
            return f(data["sub"], *args, **kwargs)
        except JWTError as e:
            print("❌ JWT Decode Error:", e)
            return jsonify({"message": "Invalid or expired token."}), 401
    return decorated

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"message": "Missing token!"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print("🧠 Decoded Token Payload (Mechanic):", data)

            if data.get("role") != "mechanic":
                return jsonify({"message": "Unauthorized role!"}), 403
            return f(data["sub"], *args, **kwargs)
        except JWTError as e:
            print("❌ JWT Decode Error:", e)
            return jsonify({"message": "Invalid or expired token."}), 401
    return decorated

def _extract_token():
    auth_header = request.headers.get("Authorization")
    if auth_header and " " in auth_header:
        return auth_header.split(" ")[1]
    return None
