import firebase_admin
from firebase_admin import credentials, auth, firestore

# Download service account key from Firebase Console
# Project Settings > Service Accounts > Generate New Private Key
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def create_user(email, password, additional_data=None):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )
        
        # Store additional user data in Firestore
        user_ref = db.collection('users').document(user.uid)
        user_data = {
            'email': email,
            'created_at': firestore.SERVER_TIMESTAMP,
            # Add any additional user profile data
            **(additional_data or {})
        }
        user_ref.set(user_data)
        
        return user.uid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user(user_id):
    try:
        # Retrieve user data from Firestore
        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get()
        return user_data.to_dict() if user_data.exists else None
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None