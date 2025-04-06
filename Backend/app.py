from flask import Flask, request, jsonify, Response
import firebase_init  # Firebase Admin initialization
from firebase_admin import auth, exceptions, db
from AutoMatchmaking import AutoMatchmaker
from flask_cors import CORS  # Import CORS
import Board as m_board
import threading
import time
import json  # Import json module for manual serialization
import random  # Add import for random symbol assignment

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
        
        # Get room data to determine player symbols
        room_ref = db.reference(f"rooms/{room_id}")
        room_data = room_ref.get()
        
        # Get current user's ID from token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 400
            
        id_token = auth_header.split('Bearer ')[1]
        user_id = verify_token(id_token)
        
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Get player's symbol (X or O)
        player_symbol = None
        if room_data and "player_symbols" in room_data:
            player_symbol = room_data["player_symbols"].get(user_id)
            
        # Convert the large board to a dictionary to send as a response
        board_data = {
            "mini_boards": [
                {"cells": [cell.state for cell in mini_board.cells], 'state': mini_board.state} 
                for mini_board in large_board.mini_boards
            ],
            "state": large_board.state,
            "turn": large_board.turn,
            "To_playboard": large_board.to_playboard,
            "player_symbol": player_symbol,  # Send player's symbol to frontend
            "is_player_turn": (player_symbol == large_board.turn)
        }

        return jsonify({"status": "success", "board": board_data}), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching board: {str(e)}"}), 500
    

# Function to trigger SSE update for the room
def trigger_sse_update(room_id, large_board):
    try:
        room_ref = db.reference(f"rooms/{room_id}")
        room_data = room_ref.get()
        
        if not room_data:
            return
        
        players = room_data['players']
        player_symbols = room_data.get('player_symbols', {})
        
        # Convert the large board to a dictionary to send as a response
        board_data = {
            "mini_boards": [
                {"cells": [cell.state for cell in mini_board.cells], 'state': mini_board.state} 
                for mini_board in large_board.mini_boards
            ],
            "state": large_board.state,
            "turn": large_board.turn,
            "To_playboard": large_board.to_playboard
        }
        
        if room_id in sse_connections:
            for user_id in players:
                if user_id in sse_connections[room_id]:
                    # Add player-specific information
                    player_board_data = dict(board_data)
                    player_board_data["player_symbol"] = player_symbols.get(user_id)
                    player_board_data["is_player_turn"] = (player_board_data["player_symbol"] == large_board.turn)
                    
                    sse_connections[room_id][user_id].append({
                        "board": player_board_data, 
                        "status": "update"
                    })
    except Exception as e:
        print(f"Error in trigger_sse_update: {e}")

# SSE endpoint to send updates to clients
@app.route('/events/<room_id>', methods=['GET'])
def sse(room_id):
    def generate(user_id):
        # Register new connections
        if room_id not in sse_connections:
            sse_connections[room_id] = {}

        if user_id not in sse_connections[room_id]:
            sse_connections[room_id][user_id] = []
            
        print(f"SSE connection established for user {user_id} in room {room_id}")

        def send_sse_data():
            try:
                while True:
                    if room_id in sse_connections and user_id in sse_connections[room_id]:
                        if sse_connections[room_id][user_id]:
                            updates = list(sse_connections[room_id][user_id])
                            sse_connections[room_id][user_id] = []
                            
                            for update in updates:
                                # Use manual JSON serialization instead of jsonify
                                # to avoid application context issues
                                try:
                                    update_json = json.dumps(update)
                                    yield f"data: {update_json}\n\n"
                                    print(f"Sent update to user {user_id}")
                                except Exception as json_err:
                                    print(f"Error serializing update: {json_err}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in SSE stream for {user_id}: {e}")
            finally:
                # Make sure to clean up the connection when done
                try:
                    clean_up_connection(room_id, user_id)
                except Exception as cleanup_err:
                    print(f"Error during connection cleanup: {cleanup_err}")

        return Response(send_sse_data(), content_type='text/event-stream')
    
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing token parameter"}), 400
    
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    return generate(user_id)

def clean_up_connection(room_id, user_id, connection=None):
    print(f"Cleaning up connection for user {user_id} in room {room_id}")
    if room_id in sse_connections:
        if user_id in sse_connections[room_id]:
            if connection is None:
                del sse_connections[room_id][user_id]
                print(f"Removed user {user_id} from room {room_id}")
        if not sse_connections[room_id]:
            del sse_connections[room_id]
            print(f"Removed room {room_id} from SSE connections")

@app.route('/update-board/<room_id>', methods=['POST'])
def update_board(room_id):
    try:
        data = request.get_json()
        mini_board_index = data.get("mini_board_index")
        cell_index = data.get("cell_index")
        value = data.get("value")  # 'X' or 'O'

        # Verify the user's identity and turn
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 400
            
        id_token = auth_header.split('Bearer ')[1]
        user_id = verify_token(id_token)
        
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Get room data to verify player symbol
        room_ref = db.reference(f"rooms/{room_id}")
        room_data = room_ref.get()
        
        if not room_data or "player_symbols" not in room_data:
            return jsonify({"error": "Room data not found or incomplete"}), 404
            
        player_symbol = room_data["player_symbols"].get(user_id)
        
        # Load the large board
        large_board = m_board.load_large_board_from_db(room_id)
        if not large_board:
            return jsonify({"error": "Board data not found"}), 404
            
        # Check if it's the player's turn
        if (player_symbol != large_board.turn):
            return jsonify({"error": "Not your turn"}), 403
            
        # Verify the value matches the player's symbol
        if value != player_symbol:
            return jsonify({"error": "Invalid move: wrong symbol"}), 400

        # Rest of the function remains the same
        result = large_board.update_mini_board(mini_board_index, cell_index, value)

        if "Invalid" in result:
            return jsonify({"error": result}), 400

        m_board.save_large_board_to_db(large_board, room_id)
        trigger_sse_update(room_id, large_board)

        large_board_winner = large_board.check_winner()
        if large_board_winner:
            return jsonify({"status": "success", "message": f"{large_board_winner} wins the game!"}), 200

        return jsonify({"status": "success", "message": "Board updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error updating board: {str(e)}"}), 500





if __name__ == "__main__":
    app.run(debug=True)
