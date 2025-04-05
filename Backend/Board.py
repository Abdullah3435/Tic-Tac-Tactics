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
        if self.is_complete():
            states = [cell.state for cell in self.cells]
            if states.count("X") == 9:
                self.state = "X"
                return "X"
            if states.count("O") == 9:
                self.state = "O"
                return "O"
        return None

    def __repr__(self):
        return "\n".join([" | ".join([str(self.cells[i + j]) for j in range(3)]) for i in range(0, 9, 3)])


class LargeBoard:
    def __init__(self):
        self.mini_boards = [MiniBoard() for _ in range(9)]
        self.state = None

    def update_mini_board(self, mini_board_index, cell_index, value):
        mini_board = self.mini_boards[mini_board_index]
        if mini_board.update_cell(cell_index, value):
            winner = mini_board.check_winner()
            if winner:
                return f"Mini-board {mini_board_index} has a winner: {winner}"
        return "Cell updated successfully"

    def check_winner(self):
        mini_board_states = [mini_board.state for mini_board in self.mini_boards]
        
        if mini_board_states.count("X") == 9:
            self.state = "X"
            return "X"
        if mini_board_states.count("O") == 9:
            self.state = "O"
            return "O"
        return None

    def __repr__(self):
        return "\n\n".join([f"Mini-board {i}:\n{repr(self.mini_boards[i])}" for i in range(9)])

    @classmethod
    def from_dict(cls, data):
        """Deserialize a dictionary into a LargeBoard object."""
        large_board = cls()
        
        # Deserialize mini boards
        for i, mini_board_data in enumerate(data["mini_boards"]):
            mini_board = MiniBoard()
            for j, cell_state in enumerate(mini_board_data["players"]):
                mini_board.cells[j] = Cell(cell_state)  # Rebuild each cell with its state
            large_board.mini_boards[i] = mini_board
        large_board.state = data["state"]
        
        return large_board


def save_large_board_to_db(large_board, room_id):
    large_board_data = {
        "mini_boards": [
            {"players": [cell.state for cell in mini_board.cells]} 
            for mini_board in large_board.mini_boards
        ],
        "state": large_board.state
    }

    db.reference(f"rooms/{room_id}/board").set(large_board_data)


def load_large_board_from_db(room_id):
    """Fetch the large board from the database and return it as a LargeBoard object."""
    ref = db.reference(f"rooms/{room_id}/board")
    data = ref.get()
    
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