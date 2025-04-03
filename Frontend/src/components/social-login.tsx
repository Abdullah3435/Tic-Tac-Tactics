import React from "react";
import { auth } from "../firebase"; // Import the Firebase auth instance
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth"; // Import the necessary Firebase authentication functions

interface SocialLoginProps {
  text: string;
  bg: string;
  border: string;
  onClickFunc?: (...args: any[]) => any; // Optional custom click handler
}

function SocialLogin({ text, bg, border, onClickFunc }: SocialLoginProps) {
  // Google Sign-In handler inside the SocialLogin component
  const handleGoogleLogin = async () => {
    const provider = new GoogleAuthProvider(); // Use the GoogleAuthProvider from the modular SDK
    try {
      const result = await signInWithPopup(auth, provider); // Use signInWithPopup from the modular SDK
      const user = result.user;
      if (user) {
        console.log("User signed in with Google:", user);
        // Handle the successful login (e.g., navigate to home page, store user data)
      }
    } catch (error) {
      // Here, we narrow the type of `error` to be an instance of `Error`
      if (error instanceof Error) {
        console.error("Error during Google sign-in:", error.message);
      } else {
        console.error("Unknown error during Google sign-in");
      }
    }
  };

  return (
    <button
      className="social-login"
      style={{ backgroundColor: `${bg}`, border: `${border}` }}
      onClick={onClickFunc || handleGoogleLogin} // Default to handleGoogleLogin if no onClickFunc provided
    >
      {text}
    </button>
  );
}

export default SocialLogin;
