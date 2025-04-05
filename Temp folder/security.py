import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import auth, credentials
import bcrypt
import jwt
from datetime import datetime, timedelta

# Secret key for JWT - MUST be kept secret and complex
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_very_complex_secret_key')

def generate_token(user_id):
    """Generate a JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def validate_token(token):
    """Validate the JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """Hash a password for storing"""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(password, hashed):
    """Check a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Input validation function
def validate_input(input_data, rules):
    """
    Validate input based on specified rules
    rules: dictionary of {field: [validation_functions]}
    """
    errors = {}
    for field, field_rules in rules.items():
        value = input_data.get(field)
        for rule in field_rules:
            if not rule['check'](value):
                errors[field] = rule['message']
                break
    return errors

# Example validation rules
SIGNUP_VALIDATION_RULES = {
    'email': [
        {
            'check': lambda x: x and '@' in x,
            'message': 'Invalid email format'
        }
    ],
    'password': [
        {
            'check': lambda x: x and len(x) >= 8,
            'message': 'Password must be at least 8 characters long'
        }
    ]
}