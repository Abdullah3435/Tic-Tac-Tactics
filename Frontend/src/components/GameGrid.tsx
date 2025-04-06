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
    // Implementation depends on your board structure
    // This is a placeholder for updating the game state from SSE data
    console.log("Updating board from SSE data:", boardData);

    // Example update logic (adjust based on your actual data structure):
    if (boardData.mini_boards) {
      // Convert the backend board format to your frontend format
      // This is just an example and needs to be adjusted
      const updatedBoards = gameBoards.map((board, index) => {
        return {
          ...board,
          Board: convertBoardFormat(boardData.mini_boards[index].players),
          BoardState: boardData.mini_boards[index].state || 0,
        };
      });

      setGameBoards(updatedBoards);
      setCurrentTurn(boardData.turn || currentTurn);
      setActiveBoard(
        boardData.To_playboard !== undefined ? boardData.To_playboard : null
      );
    }
  };

  // Helper function to convert board format (adjust based on your data structures)
  const convertBoardFormat = (players: any) => {
    // This is just a placeholder. Implement based on your actual data structure
    return players;
  };

  const handleCellClick = async (
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

      // Update the active board for the next move
      const nextActiveBoard = 3 * rowIndex + colIndex;
      if (newBoards[nextActiveBoard].BoardState === 0) {
        setActiveBoard(nextActiveBoard);
      } else {
        setActiveBoard(null);
      }

      // Switch turns
      setCurrentTurn(3 - currentTurn);

      // Update the boards locally
      setGameBoards(newBoards);

      // Send the update to the backend
      if (roomId) {
        await sendBoardUpdate(
          roomId,
          boardNum.valueOf(),
          rowIndex * 3 + colIndex,
          currentTurn
        );
      }
    }
  };

  const sendBoardUpdate = async (
    roomId: string,
    miniBoardIndex: number,
    cellIndex: number,
    value: number
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
            value: value === 1 ? "X" : "O", // Assuming 1=X and 2=O, adjust as needed
          }),
        }
      );

      const data = await response.json();
      console.log("Board update response:", data);

      if (data.status !== "success") {
        console.error("Failed to update board:", data.error);
        // You might want to revert the local board update if the server rejected it
      }
    } catch (error) {
      console.error("Error updating board:", error);
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
