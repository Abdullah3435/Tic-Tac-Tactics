# firebase_admin.py
import firebase_admin
from firebase_admin import credentials



# Initialize the Firebase Admin SDK
def initfirebase():
    cred = credentials.Certificate('/home/musab/Habib_University/6th Semester/SE/project/Tic-Tac-Tactics/Backend/tic-tac-tactics-firebase-adminsdk-fbsvc-4634b03bd5.json')
    print("firebase init")
    firebase_admin.initialize_app(cred,{'databaseURL': "https://tic-tac-tactics-default-rtdb.firebaseio.com"})
    print("firebase init done")
