import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Login() {
  const navigate = useNavigate();


  return (
    <div className="App">
      <div style={{ listStyle: 'none', display: 'flex', gap: '16px', flexDirection: 'column' }}>
        <li> Login </li>
        <li><button onClick={() => navigate('/')}> Back to Home </button></li>
      </div>      
    </div>
  );
}

export default Login;