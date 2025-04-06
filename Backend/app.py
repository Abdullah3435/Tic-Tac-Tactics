from flask import Flask, request, jsonify, Response
import firebase_init  # Firebase Admin initialization
from firebase_admin import auth, exceptions, db
from AutoMatchmaking import AutoMatchmaker
from flask_cors import CORS  # Import CORS
import Board as m_board
import threading
import time

firebase_init.initfirebase()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global storage for SSE connections (for simplicity)
sse_connections = {}

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

@app.route('/leave_room', methods=['POST'])
def leave_room():
    data = request.get_json()
    room_id = data['room_id']
    user_id = data['user_id']
    
    room_ref = db.reference(f"rooms/{room_id}")
    room_data = room_ref.get()

    if not room_data:
        return {"status": "error", "message": "Room not found"}, 404

    if user_id in room_data['players']:
        room_data['players'].remove(user_id)

        if not room_data['players']:
            room_ref.delete()  # No players left, delete room
        else:
            room_ref.update({"players": room_data['players'], "status": "waiting"})

    return {"status": "success", "message": "Player left the room"}

    
@app.route('/get-board/<room_id>', methods=['GET'])
def get_board(room_id):
    try:
        # Load the large board from the database
        large_board = m_board.load_large_board_from_db(room_id)

        if not large_board:
            return jsonify({"error": "Board data not found"}), 404
        
        # Convert the large board to a dictionary to send as a response
        board_data = {
            "mini_boards": [
                {"players": [cell.state for cell in mini_board.cells]} 
                for mini_board in large_board.mini_boards
            ],
            "state": large_board.state,
            "turn" : large_board.turn,
            "To_playboard" : large_board.to_playboard
        }

        return jsonify({"status": "success", "board": board_data}), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching board: {str(e)}"}), 500
    

# Function to trigger SSE update for the room
def trigger_sse_update(room_id, large_board):
    room_ref = db.reference(f"rooms/{room_id}")
    room_data = room_ref.get()
    
    if not room_data:
        return
    
    players = room_data['players']
    if room_id in sse_connections:
        for user_id in players:
            # Ensure user is connected before sending updates
            if user_id in sse_connections[room_id]:
                for connection in sse_connections[room_id][user_id]:
                    try:
                        connection.put({"board": large_board, "status": "update"})
                    except Exception as e:
                        print(f"Error sending SSE to user {user_id}: {e}")
                    finally:
                        # Ensure connection is removed on error or when no longer needed
                        clean_up_connection(room_id, user_id, connection)

# SSE endpoint to send updates to clients
@app.route('/events/<room_id>', methods=['GET'])
def sse(room_id):
    def generate(user_id):
        # Register new connections
        if room_id not in sse_connections:
            sse_connections[room_id] = {}

        if user_id not in sse_connections[room_id]:
            sse_connections[room_id][user_id] = []

        def send_sse_data():
            try:
                while True:
                    data = sse_connections[room_id][user_id]
                    if data:
                        for update in data:
                            yield f"data: {update}\n\n"
                    time.sleep(1)  # Prevent tight loop if no data
            except Exception as e:
                print(f"Error in SSE stream for {user_id}: {e}")
            finally:
                # Clean up when the connection is closed or an error occurs
                clean_up_connection(room_id, user_id)

        return Response(send_sse_data(), content_type='text/event-stream')
    
    # Get token from query parameters instead of Authorization header
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing token parameter"}), 400
    
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    return generate(user_id)

def clean_up_connection(room_id, user_id, connection=None):
    # Remove the connection from the tracking dictionary if it's closed or no longer valid
    if room_id in sse_connections:
        if user_id in sse_connections[room_id]:
            if connection:
                sse_connections[room_id][user_id].remove(connection)
            # Clean up the user entry if no connections are left
            if not sse_connections[room_id][user_id]:
                del sse_connections[room_id][user_id]
        # Remove the room entry if no players are left
        if not sse_connections[room_id]:
            del sse_connections[room_id]

@app.route('/update-board/<room_id>', methods=['POST'])
def update_board(room_id):
    try:
        data = request.get_json()
        mini_board_index = data.get("mini_board_index")  # Index of the mini-board (0-8)
        cell_index = data.get("cell_index")  # Index of the cell within the mini-board (0-8)
        value = data.get("value")  # The value to be set for the cell ('X' or 'O')

        # Load the large board from the database
        large_board = m_board.load_large_board_from_db(room_id)

        if not large_board:
            return jsonify({"error": "Board data not found"}), 404

        # Attempt to update the large board (this will handle mini-board updates and game logic)
        result = large_board.update_mini_board(mini_board_index, cell_index, value)

        if "Invalid" in result:  # If the update fails
            return jsonify({"error": result}), 400

        # Save the updated board data back to Firebase
        m_board.save_large_board_to_db(large_board, room_id)

        # Trigger SSE to notify users about the update
        trigger_sse_update(room_id, large_board)

        # Check if the large board has a winner
        large_board_winner = large_board.check_winner()
        if large_board_winner:
            return jsonify({"status": "success", "message": f"{large_board_winner} wins the game!"}), 200

        return jsonify({"status": "success", "message": "Board updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error updating board: {str(e)}"}), 500





if __name__ == "__main__":
    app.run(debug=True)
