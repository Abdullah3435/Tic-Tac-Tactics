# firebase_admin.py
import firebase_admin
from firebase_admin import credentials



# Initialize the Firebase Admin SDK
def initfirebase():
    cred = credentials.Certificate('tic-tac-tactics-firebase-adminsdk-fbsvc-94e569130e.json')
    print("firebase init")
    firebase_admin.initialize_app(cred,{'databaseURL': "https://tic-tac-tactics-default-rtdb.firebaseio.com"})
    print("firebase init done")
