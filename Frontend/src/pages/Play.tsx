import { useNavigate } from "react-router-dom";
import "../App.css";
import CustomButton from "../components/custom-button";
import Background from "../components/Background";
import { auth } from "../firebase"; // Firebase auth import
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth"; // Firebase functions for Google sign-in

function Play() {
  const navigate = useNavigate();
  const startPvpMatch = async () => {
    const user = auth.currentUser; // Firebase user
    if (user) {
      const idToken = await user.getIdToken(); // Get Firebase ID token

      // Send request to start the matchmaking process
      const response = await fetch("/start-pvp-match", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      if (data.status === "success") {
        // Handle room creation or joining (update UI accordingly)
        console.log("Matchmaking successful:", data.message);
        // Navigate to the game page or update UI
      } else {
        console.log("Error:", data.error);
      }
    }
  };
  return (
    <Background logo={true} footer={2}>
      <div className="App">
        <div className="vert-options">
          <li>
            <CustomButton
              text="SINGLE PLAYER"
              onClickFunc={() => navigate("/")}
            />
          </li>
          <li>
            <CustomButton text="LOCAL PVP" onClickFunc={() => navigate("/")} />
          </li>
          <li>
            <CustomButton
              text="ONLINE"
              // onClickFunc={startPvpMatch}
              onClickFunc={() => navigate("/game")}
            />
          </li>
        </div>
      </div>
    </Background>
  );
}

export default Play;
