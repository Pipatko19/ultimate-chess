
from piece_model import ChessPiece, Pawn, Rook
from king import King
from typing import Literal

class Board:
    def __init__(self, size: int = 8):
        self.size = size
        self.board: list[list[ChessPiece | None]] = [[None for _ in range(size)] for _ in range(size)]
    
    def place_piece(self, piece, col: int, row: int):
        if 0 <= col < self.size and 0 <= row < self.size:
            self.board[row][col] = piece

    def find_king_position(self, color) -> tuple[int, int]:
        for row in range(self.size):
            for col in range(self.size):
                piece = self.get_piece(col, row)
                if isinstance(piece, King) and piece.color == color:
                    return col, row
        raise ValueError(f"No {color} king found on the board.")
    
    def is_on_board(self, col: int, row: int) -> bool:
        return 0 <= col < self.size and 0 <= row < self.size
    
    def get_piece(self, col: int, row: int):
        if self.is_on_board(col, row):
            return self.board[row][col]
        return None
    
    def move_piece(self, prev_col:int, prev_row:int, next_col:int, next_row:int):
        if 0 <= prev_col < self.size and 0 <= prev_row < self.size and \
           0 <= next_col < self.size and 0 <= next_row < self.size:
            print("MOVING")
            piece = self.get_piece(prev_col, prev_row)
            self.board[next_row][next_col] = piece
            self.board[prev_row][prev_col] = None
            
            if isinstance(piece, (Pawn, King, Rook)):
                piece.first_move = False
            
            return 
        raise IndexError("Invalid board coordinates")

    
    def __iter__(self):
        return iter(self.board)
    
    def __repr__(self):
        formatted_board = ""
        for row in self:
            formatted_row = " ".join(str(piece) if piece else '.' for piece in row)
            formatted_board += formatted_row + "\n"
        return formatted_board.strip()