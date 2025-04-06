import "./GameGrid.css";

export interface GameBoardProps {
  BoardNum: Number;
  BoardState: String;
  Board: Array<string | null>; // Updated to allow null values
  onCellClick?: (boardNum: Number, cellIndex: number) => void;
  isActive?: boolean;
}

function GameBoard({
  BoardNum,
  BoardState,
  Board,
  onCellClick,
  isActive = true,
}: GameBoardProps) {
  // Render based on BoardState
  if (BoardState === "X") {
    // Show X
    return <div className="GameBoard WinX">X</div>;
  } else if (BoardState === "O") {
    // Show O
    return <div className="GameBoard WinO">O</div>;
  } else {
    // Show 3x3 grid
    return (
      <div className={`GameBoard ${isActive ? "active" : "inactive"}`}>
        {Board.map((cell, cellIndex) => (
          <div
            key={`${BoardNum}-${cellIndex}`}
            className="cell"
            onClick={() => {
              if (isActive && cell === null && onCellClick) {
                onCellClick(BoardNum, cellIndex);
              }
            }}
          >
            {cell === "X" && <span className="X">X</span>}
            {cell === "O" && <span className="O">O</span>}
            {cell === null && <span></span>}
          </div>
        ))}
      </div>
    );
  }
}

export default GameBoard;
