import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Email and password are required");
      return;
    }

    // Here you would typically make an API call to authenticate the user
    console.log("Submitting login:", { email, password });
    // For now, just navigate to dashboard or home after successful login
    navigate("/");
  };

  return (
    <div className="App">
      <div style={{ maxWidth: "400px", margin: "0 auto", padding: "20px" }}>
        <h2>Login</h2>
        {error && <div style={{ color: "red", margin: "10px 0" }}>{error}</div>}

        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "15px" }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              textAlign: "left",
            }}
          >
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ padding: "8px", fontSize: "16px" }}
            />
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              textAlign: "left",
            }}
          >
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ padding: "8px", fontSize: "16px" }}
            />
          </div>

          <button
            type="submit"
            style={{
              padding: "10px",
              backgroundColor: "#4CAF50",
              color: "white",
              border: "none",
              cursor: "pointer",
              fontSize: "16px",
            }}
          >
            Login
          </button>
        </form>

        <div style={{ marginTop: "20px" }}>
          <button onClick={() => navigate("/")} style={{ padding: "8px" }}>
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
