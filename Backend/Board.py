from firebase_admin import db

class Cell:
    def __init__(self, state=None):
        self.state = state

    def is_empty(self):
        return self.state is None

    def update(self, value):
        if self.is_empty():
            self.state = value
            return True
        return False

    def __repr__(self):
        return self.state if self.state else "None"


class MiniBoard:
    def __init__(self):
        self.cells = [Cell() for _ in range(9)]
        self.state = None

    def update_cell(self, index, value):
        if self.state is None:
            if self.cells[index].update(value):
                return True
        return False

    def is_complete(self):
        return all(cell.state is not None for cell in self.cells)

    def check_winner(self):
        """Check if the mini-board has a winner."""
        # Check all possible win conditions (rows, columns, diagonals)
        win_conditions = [
            [0, 1, 2],  # Top row
            [3, 4, 5],  # Middle row
            [6, 7, 8],  # Bottom row
            [0, 3, 6],  # Left column
            [1, 4, 7],  # Middle column
            [2, 5, 8],  # Right column
            [0, 4, 8],  # Diagonal top-left to bottom-right
            [2, 4, 6]   # Diagonal top-right to bottom-left
        ]
        
        # Check each condition for a winner
        for condition in win_conditions:
            # Get the states of the cells in the current condition
            states = [self.cells[i].state for i in condition]
            
            # If all three cells in this line are the same and not None, we have a winner
            if states[0] is not None and states[0] == states[1] == states[2]:
                self.state = states[0]  # Set the winner ("X" or "O")
                return self.state
        
        return None  # No winner yet

    def __repr__(self):
        return "\n".join([" | ".join([str(self.cells[i + j]) for j in range(3)]) for i in range(0, 9, 3)])


class LargeBoard:
    def __init__(self):
        self.mini_boards = [MiniBoard() for _ in range(9)]
        self.state = None
        self.turn = "X" # has vals 'O' or 'X'
        self.to_playboard = None # has vals 0 to 8 or None (None means play any)

    def update_mini_board(self, mini_board_index, cell_index, value):
        mini_board = self.mini_boards[mini_board_index]

        if (self.to_playboard != None) and (mini_board_index != self.to_playboard):
            return f"Invalid Board attempt allowable board is {self.to_playboard}"
        if value != self.turn:
            return f"Invalid Attempt current turn is for {self.turn}"
        
        if mini_board.update_cell(cell_index, value):
            self.turn = "O" if self.turn == "X" else "X"
            self.to_playboard = cell_index
            if self.mini_boards[self.to_playboard].state:
                self.to_playboard = None

            winner = mini_board.check_winner()
            if winner:
                return f"Mini-board {mini_board_index} has a winner: {winner}"
            return "Cell updated successfully"
        return "Invalid Move"

    def check_winner(self):
        mini_board_states = [mini_board.state for mini_board in self.mini_boards]
        
        if mini_board_states.count("X") == 9:
            self.state = "X"
            return "X"
        if mini_board_states.count("O") == 9:
            self.state = "O"
            return "O"
        return None
    
    def check_winner(self):
        """Check if the large board has a winner."""
        # Check all possible win conditions (rows, columns, diagonals)
        win_conditions = [
            [0, 1, 2],  # Top row
            [3, 4, 5],  # Middle row
            [6, 7, 8],  # Bottom row
            [0, 3, 6],  # Left column
            [1, 4, 7],  # Middle column
            [2, 5, 8],  # Right column
            [0, 4, 8],  # Diagonal top-left to bottom-right
            [2, 4, 6]   # Diagonal top-right to bottom-left
        ]
        
        # Get the states of the mini-boards (each mini-board's winner)
        mini_board_states = [mini_board.state for mini_board in self.mini_boards]
        
        # Check each condition for a winner in the large board
        for condition in win_conditions:
            states = [mini_board_states[i] for i in condition]
            
            # If all three mini-boards in this line are the same and not None, we have a winner
            if states[0] is not None and states[0] == states[1] == states[2]:
                self.state = states[0]  # Set the winner ("X" or "O")
                return self.state
        
        return None  # No winner yet

    def __repr__(self):
        return "\n\n".join([f"Mini-board {i}:\n{repr(self.mini_boards[i])}" for i in range(9)])

    @classmethod
    def from_dict(cls, data):
        """Deserialize a dictionary into a LargeBoard object."""
        large_board = cls()
        
        # Deserialize mini boards
        for i, mini_board_data in enumerate(data["mini_boards"]):
            mini_board = MiniBoard()

            # For each mini-board, handle cells and state
            for j, cell_state in enumerate(mini_board_data["cells"]):
                # If cell state is an empty string, convert it to None
                mini_board.cells[j] = Cell(cell_state if cell_state != "" else None)  # Convert empty string to None

            # For mini-board state, if it's an empty string, set it to None
            mini_board.state = mini_board_data["state"] if mini_board_data["state"] != "" else None
            
            large_board.mini_boards[i] = mini_board

        # For large board state, turn, and to_playboard, if they are empty strings, convert to None
        large_board.state = data["state"] if data["state"] != "" else None
        large_board.turn = data["turn"] if data["turn"] != "" else None
        large_board.to_playboard = data["To_playboard"] if data["To_playboard"] != "" else None

        return large_board


def save_large_board_to_db(large_board, room_id):
    large_board_data = {
        "mini_boards": [
            {
                "cells": [cell.state if cell.state is not None else "" for cell in mini_board.cells],  # Replace None with ""
                "state": mini_board.state if mini_board.state is not None else ""  # Replace None with ""
            }
            for mini_board in large_board.mini_boards
        ],
        "state": large_board.state if large_board.state is not None else "",  # Replace None with ""
        "turn": large_board.turn if large_board.turn is not None else "",  # Replace None with ""
        "To_playboard": large_board.to_playboard if large_board.to_playboard is not None else ""  # Replace None with ""
    }

    print(f"Attempting to save the board: {large_board_data}")
    db.reference(f"rooms/{room_id}/board").set(large_board_data)
    print("Board saved to Firebase.")


def jsonrep_board(large_board):
    large_board_data = {
        "mini_boards": [
            {
                "cells": [cell.state if cell.state is not None else "" for cell in mini_board.cells],  # Replace None with ""
                "state": mini_board.state if mini_board.state is not None else ""  # Replace None with ""
            }
            for mini_board in large_board.mini_boards
        ],
        "state": large_board.state if large_board.state is not None else "",  # Replace None with ""
        "turn": large_board.turn if large_board.turn is not None else "",  # Replace None with ""
        "To_playboard": large_board.to_playboard if large_board.to_playboard is not None else ""  # Replace None with ""
    }

    return large_board_data


def load_large_board_from_db(room_id):
    """Fetch the large board from the database and return it as a LargeBoard object."""
    ref = db.reference(f"rooms/{room_id}/board")
    data = ref.get()
    # print(data)
    
    if data:
        return LargeBoard.from_dict(data)  # Deserialize data into LargeBoard
    return None


def initialize_empty_large_board():
    """
    Initialize an empty LargeBoard with all mini-boards empty.
    """
    large_board = LargeBoard()

    # Set the state of each mini-board to None (unplayed)
    for mini_board in large_board.mini_boards:
        mini_board.state = None  # Ensure mini-boards are in the 'None' state
    
    # Set the state of the large board to None (game hasn't been won yet)
    large_board.state = None
    return large_board