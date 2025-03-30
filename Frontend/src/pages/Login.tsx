import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import "./card.css";
import Background from "../components/Background";
import SocialLogin from "../components/social-login";
import CircularButton from "../components/circular-button";

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
    <Background logo={false} footer={1}>
      <div className="App">
        {/* Tic Tac Tactics text */}
        <div
          className="login-card flex flex-col justify-center items-center"
          style={{ position: "relative" }}
        >
          {/* Back to home button - top left */}
          <div
            style={{
              position: "absolute",
              top: "15px",
              left: "15px",
            }}
          >
            <CircularButton icon="HiX" onClickFunc={() => navigate("/")} />
          </div>

          <img
            src="assets/Logo-text.png"
            alt="Tic-Tac-Tactics Logo"
            style={{ width: "60%", marginBottom: "20px" }}
          />

          {/* Log in using email & password */}
          <h2 className="text-4xl">LOG IN</h2>
          <div
            style={{
              color: "red",
              margin: "10px 0",
              height: "20px",
              minHeight: "20px",
            }}
          >
            {error}
          </div>

          {/* Form for login */}
          <form
            onSubmit={handleSubmit}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "15px",
              width: "100%",
              position: "relative",
            }}
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
                className="input-field"
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
                className="input-field"
              />
            </div>
            <div
              style={{
                position: "absolute",
                bottom: "0px",
                right: "15px",
              }}
            >
              <CircularButton icon="HiArrowRight" onClickFunc={handleSubmit} />
            </div>
          </form>

          {/* Separator */}
          <div style={{ margin: "20px 0", width: "100%" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                margin: "20px 0",
              }}
            >
              <div
                style={{ flex: 1, height: "1px", backgroundColor: "#ccc" }}
              ></div>
              <span style={{ margin: "0 10px", color: "#fff" }}>
                Sign in using
              </span>
              <div
                style={{ flex: 1, height: "1px", backgroundColor: "#ccc" }}
              ></div>
            </div>

            {/* Social Login Buttons */}
            <div
              style={{ display: "flex", justifyContent: "center", gap: "15px" }}
            >
              <SocialLogin
                text="Google"
                bg="#db4437"
                border="1px solid #db4437"
                onClickFunc={() => console.log("Google login clicked")}
              />
              <SocialLogin
                text="Facebook"
                bg="#3b5998"
                border="1px solid #3b5998"
                onClickFunc={() => console.log("Facebook login clicked")}
              />
            </div>
          </div>
        </div>
      </div>
    </Background>
  );
}

export default Login;
