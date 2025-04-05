# import React from 'react';
# import { GoogleLogin } from '@react-oauth/google';
# import { GoogleOAuthProvider } from '@react-oauth/google';

# function GoogleLoginButton() {
#   const clientId = 'YOUR_GOOGLE_CLIENT_ID';  #Replace with your actual Google Client ID

#   const handleSuccess = (credentialResponse) => {
#     console.log(credentialResponse);
    
#     # // Send the credential to your backend for verification
#     fetch('http://localhost:5000/login/google', {
#       method: 'POST',
#       headers: {
#         'Content-Type': 'application/json',
#       },
#       body: JSON.stringify({ 
#         credential: credentialResponse.credential 
#       })
#     })
#     .then(response => response.json())
#     .then(data => {
#       // Handle successful login (e.g., store token, redirect)
#       console.log('Login successful:', data);
#     })
#     .catch(error => {
#       console.error('Login failed:', error);
#     });
#   };

#   const handleError = () => {
#     console.log('Login Failed');
#   };

#   return (
#     <GoogleOAuthProvider clientId={clientId}>
#       <GoogleLogin
#         onSuccess={handleSuccess}
#         onError={handleError}
#       />
#     </GoogleOAuthProvider>
#   );
# }

# export default GoogleLoginButton;

# // src/context/AuthContext.tsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

# // Define types
type User = {
  id: string;
  email: string;
  name: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  error: string | null;
  signup: (email: string, password: string, name: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  logout: () => Promise<void>;
};

# // Set up API client
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

# // Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

# // Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

# // Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await api.get('/auth/me');
        setUser(res.data);
      } catch (err) {
        // Invalid token - remove it
        localStorage.removeItem('token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Signup function
  const signup = async (email: string, password: string, name: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await api.post('/auth/signup', { email, password, name });
      setUser(res.data);
      localStorage.setItem('token', res.data.token);
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred during signup');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  # // Login function
  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await api.post('/auth/login', { email, password });
      setUser(res.data);
      localStorage.setItem('token', res.data.token);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid credentials');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  # // Google login function
  const googleLogin = async (credential: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await api.post('/auth/google-auth', { credential });
      setUser(res.data);
      localStorage.setItem('token', res.data.token);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Google authentication failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  # // Logout function
  const logout = async () => {
    setLoading(true);
    
    try {
      localStorage.removeItem('token');
      setUser(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Logout failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, signup, login, googleLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

# // Custom hook for using the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

# // Updated Login component integrating your existing Google component
# // src/components/Login.tsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import { GoogleOAuthProvider } from '@react-oauth/google';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, googleLogin, error, loading } = useAuth();
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      # // Navigate to dashboard or home page after successful login
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      await googleLogin(credentialResponse.credential);
      # // Navigate to dashboard or home page after successful login
    } catch (err) {
      console.error('Google login failed:', err);
    }
  };

  const handleGoogleError = () => {
    console.error('Google sign-in was unsuccessful');
  };

  return (
    <div className="auth-form">
      <h2>Login</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <div className="separator">OR</div>
      
      <div className="google-auth">
        <GoogleOAuthProvider clientId={clientId}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
          />
        </GoogleOAuthProvider>
      </div>
    </div>
  );
};

export default Login;