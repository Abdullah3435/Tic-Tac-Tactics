import uuid
from datetime import datetime, timedelta
from firebase_admin import db
import Board

class AutoMatchmaker:
    def __init__(self):
        self.db_ref = db.reference("rooms")  # Firebase Realtime Database reference

    def start_matchmaking(self, user_id):
        """
        Start the matchmaking process by either finding an available room or creating a new room.
        """
        # Check if there's a room with only one player waiting
        # existing_room = self.find_available_room()
        existing_room = self.find_available_room(user_id)


        if existing_room:
            # If a room exists, add the player to that room
            self.join_existing_room(existing_room['room_id'], user_id)
            return {"status": "success", "message": f"Joined room {existing_room['room_id']}", "room_id" : f"{existing_room['room_id']}"  } 
        else:
            # If no room exists, create a new one and wait for the second player to join
            new_room_id = self.create_new_room(user_id)
            return {"status": "success", "message": f"Room created: {new_room_id}, waiting for second player", "room_id" : new_room_id }

    # def find_available_room(self):
    #     """
    #     Check if there are any rooms with only one player waiting for a match.
    #     """
    #     rooms = self.db_ref.get()  # Fetch rooms from Firebase
    #     if rooms is None:
    #         return None
    #     for room_id, room_data in rooms.items():
    #         if len(room_data['players']) == 1 and user_id not in room_data['players']:
    #             return {"room_id": room_id, "players": room_data['players']}


    #     for room_id, room_data in rooms.items():
    #         if len(room_data['players']) == 1:  # Check if room has only 1 player
    #             return {"room_id": room_id, "players": room_data['players']}
    #     return None
    def find_available_room(self, user_id):
        """
        Check if there are any rooms with only one player waiting for a match,
        and make sure the user is not already in that room.
        """
        rooms = self.db_ref.get()  # Fetch rooms from Firebase
        if rooms is None:
            return None

        for room_id, room_data in rooms.items():
            if len(room_data['players']) == 1 and user_id not in room_data['players']:
                return {"room_id": room_id, "players": room_data['players']}
        
        return None


    def join_existing_room(self, room_id, user_id):
        """
        Add a player to an existing room.
        """
        room_ref = self.db_ref.child(room_id)
        room_data = room_ref.get()
        
        # Add the user to the room and update the status
        room_data['players'].append(user_id)
        room_data['status'] = "started"  # The game starts when 2 players are in the room
        
        room_ref.update(room_data)
        return room_data  # Return updated room data

    def create_new_room(self, user_id):
        """
        Create a new room and add the first player, also initialize the board.
        """
        room_id = str(uuid.uuid4())  # Generate a unique room ID
        large_board = Board.initialize_empty_large_board()
        print (large_board)

        room_data = {
            "room_id": room_id,
            "players": [user_id],  # Add the first player to the room
            "status": "waiting",   # Room is waiting for a second player
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  # Store the creation timestamp
            "board" : Board.jsonrep_board(large_board)
        }

        # Add the room to Firebase
        self.db_ref.child(room_id).set(room_data)

        # Wait for the second player to join (blocking until the room is full)
        self.wait_for_second_player(room_id)

        return room_id  # Return the newly created room ID

    def wait_for_second_player(self, room_id):
        """
        Block and wait for the second player to join the room.
        """
        room_ref = self.db_ref.child(room_id)
        
        while True:
            room_data = room_ref.get()
            if len(room_data['players']) == 2:  # Check if the room has both players
                room_ref.update({'status': 'ready'})  # Mark the room as ready
                break  # Exit the loop when the second player joins
            else:
                # Optionally, you can handle timeouts here (e.g., abort room creation if no second player joins in X minutes)
                pass

        # The room is now ready with two players

