from flask import Flask, request, jsonify
import firebase_init  # Firebase Admin initialization
from firebase_admin import auth, exceptions,db
from AutoMatchmaking import AutoMatchmaker
from flask_cors import CORS  # Import CORS
import Board as m_board

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
            "state": large_board.state
        }

        return jsonify({"status": "success", "board": board_data}), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching board: {str(e)}"}), 500
    
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
        
        # Check if the mini-board index is valid
        if mini_board_index < 0 or mini_board_index > 8:
            return jsonify({"error": "Invalid mini-board index"}), 400

        mini_board = large_board.mini_boards[mini_board_index]
        
        # Check if the cell index is valid
        if cell_index < 0 or cell_index > 8:
            return jsonify({"error": "Invalid cell index"}), 400

        # Check if the mini-board is ready (if X or O already filled, block updates)
        if mini_board.state in ["X", "O"]:
            return jsonify({"error": "Cannot update a completed mini-board"}), 400
        
        # Update the specific cell
        cell_updated = mini_board.update_cell(cell_index, value)

        if not cell_updated:
            return jsonify({"error": "Cell update failed (possibly already occupied)"}), 400

        # Check if mini-board has a winner
        winner = mini_board.check_winner()
        if winner:
            mini_board.state = winner  # Update mini-board state to X or O if there's a winner

        # Save the updated board data back to Firebase
        m_board.save_large_board_to_db(large_board, room_id)

        return jsonify({"status": "success", "message": "Board updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error updating board: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)
