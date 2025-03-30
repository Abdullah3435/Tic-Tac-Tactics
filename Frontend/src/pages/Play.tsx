import { useNavigate } from "react-router-dom";
import "../App.css";
import CustomButton from "../components/custom-button";
import Background from "../components/Background";

function Play() {
  const navigate = useNavigate();

  return (
    <Background footer={2}>
      <div className="App">
        <div className="vert-options">
          <li>
            <CustomButton
              text="SINGLE PLAYER"
              onClickFunc={() => navigate("/login")}
            />
          </li>
          <li>
            <CustomButton
              text="LOCAL PVP"
              //   onClickFunc={() => navigate("/signup")}
            />
          </li>
          <li>
            <CustomButton text="ONLINE" onClickFunc={() => navigate("/")} />
          </li>
        </div>
      </div>
    </Background>
  );
}

export default Play;
