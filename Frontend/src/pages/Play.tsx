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
    if (!user) {
      console.log("User is not signed in.");
      return;
    }

    try {
      const idToken = await user.getIdToken(); // Get Firebase ID token

      // Send request to start the matchmaking process
      const response = await fetch("http://127.0.0.1:5000/start-pvp-match", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status === "success") {
        console.log("Room creation successful:", data.message);

        // Store room ID in localStorage for use in the game component
        localStorage.setItem("roomId", data.room_id);
        console.log("Room ID stored in localStorage:", data.room_id);

        // Store token for SSE connection
        localStorage.setItem("userToken", idToken);

        // Navigate to game page (SSE connection will be handled in GameGrid)
        navigate("/game");
      } else {
        console.log("Error:", data.error);
      }
    } catch (error) {
      console.error("Failed to start PvP match:", error);
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
            <CustomButton text="ONLINE" onClickFunc={startPvpMatch} />
          </li>
        </div>
      </div>
    </Background>
  );
}

export default Play;
