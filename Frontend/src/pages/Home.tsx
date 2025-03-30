import { useNavigate } from "react-router-dom";
import "../App.css";
import CustomButton from "../components/custom-button";
import Background from "../components/Background";

function Home() {
  const navigate = useNavigate();

  return (
    <Background>
      <div className="App">
        <div className="vert-options">
          <li>
            <CustomButton
              text="LOG IN"
              onClickFunc={() => navigate("/login")}
            />
          </li>
          <li>
            <CustomButton
              text="SIGN UP"
              onClickFunc={() => navigate("/signup")}
            />
          </li>
          <li>
            <CustomButton
              text="SETTINGS"
              onClickFunc={() => navigate("/signup")}
              size="small"
            />
          </li>
        </div>
      </div>
    </Background>
  );
}

export default Home;
