// src/firebase.ts
import { initializeApp } from 'firebase/app';  // Import initializeApp for Firebase app initialization
import { getAuth } from 'firebase/auth';         // Import getAuth for Authentication
import { getDatabase } from 'firebase/database'; // Import getDatabase for Realtime Database
// Or import Firestore if you're using Firestore: 
// import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyBq_EXzgyoEgvjoNemDZJZAJdBTtZwjwsk",
    authDomain: "tic-tac-tactics.firebaseapp.com",
    databaseURL: "https://tic-tac-tactics-default-rtdb.firebaseio.com",
    projectId: "tic-tac-tactics",
    storageBucket: "tic-tac-tactics.firebasestorage.app",
    messagingSenderId: "1008927253189",
    appId: "1:1008927253189:web:d51cb67df5bfab5ee186ac",
    measurementId: "G-YPCYTLPN8Q"
  };

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);  // Initialize the Firebase app

// Get Firebase services
const auth = getAuth(firebaseApp);  // Get the authentication service
const db = getDatabase(firebaseApp); // Get the Realtime Database service
// Or Firestore if you're using Firestore
// const db = getFirestore(firebaseApp);

export { auth, db };