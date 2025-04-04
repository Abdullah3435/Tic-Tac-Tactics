from flask import Flask, request, jsonify
import firebase_init  # Firebase Admin initialization
from firebase_admin import auth, exceptions
from AutoMatchmaking import AutoMatchmaker
from flask_cors import CORS  # Import CORS

firebase_init.initfirebase()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Middleware to verify Firebase ID Token
def verify_token(id_token):
    try:
        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']  # Extract UID from the token
        return uid  # Return the user ID if token is valid
    except exceptions.FirebaseError as e:
        print(f"Error verifying token: {e}")
        return None  # Return None if token verification fails

@app.route('/')
def hello_world():
    return jsonify(message="Hello World")

@app.route('/start-pvp-match', methods=['POST'])
def start_pvp_match():
    # Extract the token from the Authorization header
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 400

    # Remove 'Bearer ' prefix from the Authorization header
    if auth_header.startswith('Bearer '):
        id_token = auth_header.split('Bearer ')[1]
    else:
        return jsonify({"error": "Invalid token format, must be Bearer <token>"}), 400

    # Verify the Firebase ID token
    user_id = verify_token(id_token)
    
    if not user_id:
        return jsonify({"error": "Unauthorized", "message": "Invalid or expired token"}), 401
    
    # Initialize the AutoMatchmaker
    matchmaker = AutoMatchmaker()

    print ("Matchmaking started")
    # Start the matchmaking process
    result = matchmaker.start_matchmaking(user_id)
    print ("Matchmaking ended")

    # Respond back with the matchmaking result
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
