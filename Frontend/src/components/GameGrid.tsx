import { useState } from "react";
import "./GameGrid.css";
import GameBoard, { GameBoardProps } from "./GameBoard";

export interface GameGridProps {
  GameBoards: Array<GameBoardProps>;
  initialTurn?: number;
}

function GameGrid({
  GameBoards: initialGameBoards,
  initialTurn = 1,
}: GameGridProps) {
  const [gameBoards, setGameBoards] =
    useState<Array<GameBoardProps>>(initialGameBoards);
  const [currentTurn, setCurrentTurn] = useState<number>(initialTurn);
  const [activeBoard, setActiveBoard] = useState<Number | null>(null);

  const handleCellClick = (
    boardNum: Number,
    rowIndex: number,
    colIndex: number
  ) => {
    // Make a deep copy of the boards
    const newBoards = JSON.parse(JSON.stringify(gameBoards));
    const boardIndex = newBoards.findIndex(
      (board: GameBoardProps) => board.BoardNum === boardNum
    );

    if (boardIndex !== -1) {
      // Update the cell with current player's mark
      newBoards[boardIndex].Board[rowIndex][colIndex] = currentTurn;

      // Check if the move resulted in a win on this board
      // For now we're just updating the board without win check logic

      // Update the active board for the next move (the board corresponding to the clicked cell)
      const nextActiveBoard = 3 * rowIndex + colIndex;
      if (newBoards[nextActiveBoard].BoardState === 0) {
        setActiveBoard(nextActiveBoard);
      } else {
        setActiveBoard(null);
      }

      // Switch turns
      setCurrentTurn(3 - currentTurn);

      // Update the boards
      setGameBoards(newBoards);
    }
  };

  return (
    <div className="GameGrid">
      {gameBoards.map((board, index) => (
        <GameBoard
          key={index}
          BoardNum={board.BoardNum}
          BoardState={board.BoardState}
          Board={board.Board}
          onCellClick={handleCellClick}
          isActive={activeBoard === null || activeBoard === board.BoardNum}
        />
      ))}
    </div>
  );
}

export default GameGrid;
