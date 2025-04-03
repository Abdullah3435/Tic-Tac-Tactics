import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Play from "./pages/Play";
import Game from "./pages/Game";

const Router = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/play" element={<Play />} />
      <Route path="/game" element={<Game />} />
    </Routes>
  </BrowserRouter>
);

export default Router;
