import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Home() {
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch the Hello World message from Flask backend
    fetch('http://localhost:5000/')
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => console.error('Error fetching message:', error));
  }, []);

  return (
    <div className="App">
      <h1>{message ? message : "Loading..."}</h1>
      <div style={{ listStyle: 'none', display: 'flex', gap: '16px', flexDirection: 'column' }}>
        <li> Home </li>
        <li><button onClick={() => navigate('/login')}> Login </button> </li>
        <li><button onClick={() => navigate('/signup')}> Signup </button> </li>
      </div>      
    </div> 
  );
}

export default Home;