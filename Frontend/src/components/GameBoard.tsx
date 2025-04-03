import "./GameGrid.css";

export interface GameBoardProps {
  BoardNum: Number;
  BoardState: Number;
  Board: Array<Array<Number>>;
  onCellClick?: (boardNum: Number, rowIndex: number, colIndex: number) => void;
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
  if (BoardState === 1) {
    // Show X
    return <div className="GameBoard WinX">X</div>;
  } else if (BoardState === 2) {
    // Show O
    return <div className="GameBoard WinO">O</div>;
  } else {
    // Show 3x3 grid
    return (
      <div className={`GameBoard ${isActive ? "active" : "inactive"}`}>
        {Board.map((row, rowIndex) =>
          row.map((cell, colIndex) => (
            <div
              key={`${BoardNum}-${3 * rowIndex + colIndex}`}
              className="cell"
              onClick={() => {
                if (isActive && cell === 0 && onCellClick) {
                  onCellClick(BoardNum, rowIndex, colIndex);
                }
              }}
            >
              {cell === 1 && <span className="X">X</span>}
              {cell === 2 && <span className="O">O</span>}
              {cell === 0 && <span></span>}
            </div>
          ))
        )}
      </div>
    );
  }
}

export default GameBoard;
