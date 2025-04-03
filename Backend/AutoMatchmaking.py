import uuid
from firebase_admin import db

class AutoMatchmaker:
    def __init__(self):
        self.db_ref = db.reference("rooms")  # Firebase Realtime Database reference

    def start_matchmaking(self, user_id):
        # Check if there's a room with only one player waiting
        existing_room = self.find_available_room()
        
        if existing_room:
            # If a room exists, add the player to that room
            self.join_existing_room(existing_room['room_id'], user_id)
            return {"status": "success", "message": f"Joined room {existing_room['room_id']}"}
        else:
            # If no room exists, create a new one
            new_room_id = self.create_new_room(user_id)
            return {"status": "success", "message": f"Room created: {new_room_id}"}

    def find_available_room(self):
        """
        Check if there are any rooms with only one player waiting for a match.
        """
        rooms = self.db_ref.get()
        for room_id, room_data in rooms.items():
            if len(room_data['players']) == 1:  # Check if room has only 1 player
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
        Create a new room and add the first player.
        """
        room_id = str(uuid.uuid4())  # Generate a unique room ID
        room_data = {
            "room_id": room_id,
            "players": [user_id],  # Add the first player to the room
            "status": "waiting",   # Room is waiting for a second player
        }
        
        self.db_ref.child(room_id).set(room_data)
        return room_id  # Return the newly created room ID
