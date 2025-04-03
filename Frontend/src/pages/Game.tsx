import "../App.css";
import Background from "../components/Background";
import GameGrid from "../components/GameGrid";
import { auth } from "../firebase"; // Firebase auth import
import { useState } from "react";
import { gameBoards } from "../data/gameData";

function Game() {
  return (
    <Background logo={false} footer={1}>
      <GameGrid GameBoards={gameBoards} />
    </Background>
  );
}

export default Game;
