from flask import Flask, request, jsonify
import firebase_init  # Import the new firebase_init module that handles Firebase Admin initialization
from firebase_admin import auth, exceptions  # Import only the components you need from firebase_admin
from AutoMatchmaking import AutoMatchmaker

app = Flask(__name__)

# Middleware to verify Firebase ID Token
def verify_token(id_token):
    try:
        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']  # You can get the user ID if needed
        return uid  # Return user ID if token is valid
    except exceptions.FirebaseError as e:
        print(f"Error verifying token: {e}")
        return None  # Token verification failed


@app.route('/protected', methods=['GET'])
def protected():
    # Get the token from the request header (Assuming it's passed in the Authorization header)
    id_token = request.headers.get('Authorization')

    if not id_token:
        return jsonify({"error": "Missing token"}), 400

    # Remove "Bearer " if it's included in the Authorization header
    if id_token.startswith('Bearer '):
        id_token = id_token[7:]

    # Verify the token
    uid = verify_token(id_token)

    if uid:
        return jsonify({"message": f"Hello, user {uid}!"}), 200
    else:
        return jsonify({"error": "Invalid token"}), 401


@app.route('/start-pvp-match', methods=['POST'])
def start_pvp_match():
    # Get the Firebase ID token from the request headers (Authorization header)
    id_token = request.headers.get('Authorization').split('Bearer ')[1]
    
    try:
        # Verify the Firebase ID token and get the user UID
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
    except Exception as e:
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401
    
    # Initialize the AutoMatchmaker
    matchmaker = AutoMatchmaker()

    # Start the matchmaking process
    result = matchmaker.start_matchmaking(user_id)

    # Respond back to the frontend with the result
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
