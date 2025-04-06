import { useState, useEffect } from "react";
import "./GameGrid.css";
import GameBoard, { GameBoardProps } from "./GameBoard";
import { auth } from "../firebase"; // Import Firebase auth

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
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [playerSymbol, setPlayerSymbol] = useState<string | null>(null);
  const [isPlayerTurn, setIsPlayerTurn] = useState<boolean>(false);
  const [gameStatus, setGameStatus] = useState<string>("");

  // Initialize SSE connection on component mount
  useEffect(() => {
    const storedRoomId = localStorage.getItem("roomId");
    if (storedRoomId) {
      setRoomId(storedRoomId);
      initSSE(storedRoomId);

      // Fetch initial board state
      fetchBoardState(storedRoomId);
    }

    // Clean up on component unmount
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, []);

  const initSSE = async (roomId: string) => {
    try {
      const user = auth.currentUser;
      if (!user) {
        console.error("User not authenticated");
        return;
      }

      const idToken = await user.getIdToken();

      // Use token as a query parameter instead of Authorization header
      const es = new EventSource(
        `http://127.0.0.1:5000/events/${roomId}?token=${idToken}`
      );

      console.log("SSE initialized for room:", roomId);

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("SSE Update received in GameGrid:", data);

          if (data.board) {
            // Update the game boards based on SSE data
            updateBoardFromSSE(data.board);
          }
        } catch (error) {
          console.error("Error processing SSE message:", error);
        }
      };

      es.onerror = (error) => {
        console.error("SSE Error in GameGrid:", error);
        es.close();
      };

      setEventSource(es);
    } catch (error) {
      console.error("Failed to initialize SSE in GameGrid:", error);
    }
  };

  const fetchBoardState = async (roomId: string) => {
    try {
      const user = auth.currentUser;
      if (!user) {
        console.error("User not authenticated");
        return;
      }

      const idToken = await user.getIdToken();
      const response = await fetch(
        `http://127.0.0.1:5000/get-board/${roomId}`,
        {
          headers: {
            Authorization: `Bearer ${idToken}`,
          },
        }
      );

      const data = await response.json();
      if (data.status === "success") {
        console.log("Initial board state:", data.board);
        updateBoardFromSSE(data.board);
      } else {
        console.error("Failed to fetch board state:", data.error);
      }
    } catch (error) {
      console.error("Error fetching board state:", error);
    }
  };

  const updateBoardFromSSE = (boardData: any) => {
    console.log("Updating board from SSE data:", boardData);

    if (boardData.mini_boards) {
      // Convert the backend board format to your frontend format
      const updatedBoards = gameBoards.map((board, index) => {
        return {
          ...board,
          Board: convertCellsToStringArray(boardData.mini_boards[index].cells),
          BoardState: boardData.mini_boards[index].state || 0,
        };
      });

      setGameBoards(updatedBoards);
      setCurrentTurn(boardData.turn || currentTurn);

      if (
        boardData.To_playboard !== undefined &&
        boardData.To_playboard !== -1
      ) {
        setActiveBoard(boardData.To_playboard);
      } else {
        setActiveBoard(null);
      }

      // Update player-specific information
      if (boardData.player_symbol !== undefined) {
        setPlayerSymbol(boardData.player_symbol);
      }

      if (boardData.is_player_turn !== undefined) {
        setIsPlayerTurn(boardData.is_player_turn);
      }
    }
  };

  // Helper function to convert cell values from backend format to frontend format
  const convertCellsToStringArray = (cells: any[]) => {
    // Convert numerical values to strings and null for empty cells
    return cells.map((cell) => {
      if (cell === 0 || cell === null) return null;
      if (cell === 1) return "X";
      if (cell === 2) return "O";
      return cell.toString(); // Handle any other case
    });
  };

  const handleCellClick = async (boardNum: Number, cellIndex: number) => {
    // Check if it's the player's turn
    if (!isPlayerTurn) {
      setGameStatus("Wait for your turn!");
      return;
    }

    // Make a deep copy of the boards
    const newBoards = JSON.parse(JSON.stringify(gameBoards));
    const boardIndex = newBoards.findIndex(
      (board: GameBoardProps) => board.BoardNum === boardNum
    );

    if (boardIndex !== -1) {
      // Update the cell with player's symbol
      newBoards[boardIndex].Board[cellIndex] = playerSymbol;

      // Update the active board for the next move
      if (newBoards[cellIndex].BoardState === 0) {
        setActiveBoard(cellIndex);
      } else {
        setActiveBoard(null);
      }

      // No need to switch turns locally - will be updated via SSE
      setIsPlayerTurn(false);

      // Update the boards locally
      setGameBoards(newBoards);

      // Send the update to the backend
      if (roomId) {
        await sendBoardUpdate(
          roomId,
          boardNum.valueOf(),
          cellIndex,
          playerSymbol || ""
        );
      }
    }
  };

  const sendBoardUpdate = async (
    roomId: string,
    miniBoardIndex: number,
    cellIndex: number,
    value: string
  ) => {
    try {
      const user = auth.currentUser;
      if (!user) {
        console.error("User not authenticated");
        return;
      }

      const idToken = await user.getIdToken();

      const response = await fetch(
        `http://127.0.0.1:5000/update-board/${roomId}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mini_board_index: miniBoardIndex,
            cell_index: cellIndex,
            value: value,
          }),
        }
      );

      const data = await response.json();
      console.log("Board update response:", data);

      if (data.status !== "success") {
        console.error("Failed to update board:", data.error);
        setGameStatus(data.error || "Error updating board");
        // Revert the local board update if the server rejected it
        fetchBoardState(roomId);
      } else if (data.message) {
        // setGameStatus(data.message);
        setGameStatus("");
      }
    } catch (error) {
      console.error("Error updating board:", error);
      setGameStatus("Network error. Try again.");
    }
  };

  return (
    <div className="game-container">
      <div className="game-info">
        {gameStatus && <div className="game-status">{gameStatus}</div>}
        <div className="player-info">
          Your symbol: {playerSymbol || "Loading..."}
          <span className={isPlayerTurn ? "your-turn" : "waiting"}>
            {isPlayerTurn ? "Your Turn" : "Opponent's Turn"}
          </span>
        </div>
      </div>
      <div className="GameGrid">
        {gameBoards.map((board, index) => (
          <GameBoard
            key={index}
            BoardNum={board.BoardNum}
            BoardState={board.BoardState}
            Board={board.Board}
            onCellClick={handleCellClick}
            isActive={
              (activeBoard === null || activeBoard === board.BoardNum) &&
              isPlayerTurn
            }
          />
        ))}
      </div>
    </div>
  );
}

export default GameGrid;
