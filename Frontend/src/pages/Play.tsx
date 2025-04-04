import { useNavigate } from "react-router-dom";
import "../App.css";
import CustomButton from "../components/custom-button";
import Background from "../components/Background";
import { auth } from "../firebase"; // Firebase auth import
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth"; // Firebase functions for Google sign-in

function Play() {
  const navigate = useNavigate();
  const startPvpMatch = async () => {
    const user = auth.currentUser;  // Firebase user
    if (!user) {
      console.log("User is not signed in.");
      return;
    }
  
    if (user) {
      const idToken = await user.getIdToken();  // Get Firebase ID token
  
      // Send request to start the matchmaking process
      const response = await fetch("http://127.0.0.1:5000/start-pvp-match", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${idToken}`,
          "Content-Type": "application/json",
        },
      });
  
      const data = await response.json();
  
      // blocking until the room is created for both players

      if (data.status === "success") {
        console.log("Room creation successful:", data.message);
  
        navigate("/game") // very bad code currently we just go with it for now

        // Proceed with the game start logic after both players are in the room
        // Backend has ensured both players are in the room by now
        // Example: Navigate to the game page
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
              onClickFunc={startPvpMatch}
              //onClickFunc={() => navigate("/game")}
            />
          </li>
        </div>
      </div>
    </Background>
  );
}

export default Play;