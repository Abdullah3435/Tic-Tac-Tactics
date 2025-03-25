import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Signup() {
  const navigate = useNavigate();


  return (
    <div className="App">
      <div style={{ listStyle: 'none', display: 'flex', gap: '16px', flexDirection: 'column' }}>
        <li> Signup </li>
        <li><button onClick={() => navigate('/')}> Back to Home </button></li>
      </div>      
    </div>
  );
}

export default Signup;