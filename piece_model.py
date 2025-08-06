from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod, ABC

if TYPE_CHECKING:
    from board import Board

class FirstMoveMixin:
    """
    Mixin class to handle the first move logic for chess pieces.
    This can be used to implement special rules for pieces that have a different behavior on their first move.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_move = True
    
    def update_pos(self, **kwargs):
        """Updates the position of the piece based on its coordinates in the board state."""
        starting = kwargs.get('starting', False)
        if not starting:
            self.first_move = False  # After the first move, set first_move to False


class ChessPiece(ABC):
    
    @abstractmethod
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        """
        Abstract method to get valid moves for the piece.
        :return: A list of valid moves.
        """ 
        pass
    
    def __init__(self, color: str):
        self.color = color

class Rook(FirstMoveMixin, ChessPiece):

    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        valid_moves = set()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

        for dx, dy in directions:
            col, row = this_col + dx, this_row + dy
            while board_state.is_on_board(col, row) and board_state.get_piece(col, row) is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if board_state.is_on_board(col, row):
                valid_moves.add((col, row))
                

        return valid_moves
    def __repr__(self):
        return "R"

class Knight(ChessPiece):
    
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        moves = {
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        }
        valid_moves = set()
        for dx, dy in moves:
            col, row = this_col + dx, this_row + dy
            if board_state.is_on_board(col, row):
                valid_moves.add((col, row))
        
        return valid_moves
    def __repr__(self):
        return "N"

class Bishop(ChessPiece):
    
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        valid_moves = set()
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]  # diagonal

        for dx, dy in directions:
            col, row = this_col + dx, this_row + dy
            while board_state.is_on_board(col, row) and board_state.get_piece(col, row) is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if board_state.is_on_board(col, row):
                valid_moves.add((col, row))
        return valid_moves
    def __repr__(self):
        return "B"

class Queen(ChessPiece):
    
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        valid_moves = set()
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # horizontal and vertical
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # diagonal
        ]
        for dx, dy in directions:
            col, row = this_col + dx, this_row + dy
            while board_state.is_on_board(col, row) and board_state.get_piece(col, row) is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if board_state.is_on_board(col, row):
                valid_moves.add((col, row))
        return valid_moves
    def __repr__(self):
        return "Q"


class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.first_move = True
    
    def promote(self):
        print('LOL NIC zatim')
    
    def chech_promote(self, row):
        if row == 0 or row == 7:
            self.promote()
    
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        valid_moves = set()
        direction = 1 if self.color == "black" else -1
        if board_state.get_piece(this_col, this_row + direction) is None:
            valid_moves.add((this_col, this_row + direction))
        
        if 0 <= this_row + direction < 8 and 0 <= this_col - 1 < 8 \
            and board_state.get_piece(this_col - 1, this_row + direction) is not None:
            valid_moves.add((this_col - 1, this_row + direction))
        if 0 <= this_row + direction < 8 and 0 <= this_col + 1 < 8 \
            and board_state.get_piece(this_col + 1, this_row + direction) is not None:
            valid_moves.add((this_col + 1, this_row + direction)) 
        
        if self.first_move and board_state.get_piece(this_col,this_row + 2 * direction) is None:
            valid_moves.add((this_col, this_row + 2 * direction))
        
        return valid_moves
    def __repr__(self):
        return "P"


class TestPiece(ChessPiece):
    sprite_path = "images/{color}/test.png"

    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        # Placeholder implementation for valid moves
        return {(i, j) for i in range(8) for j in range(8)}

    def __repr__(self):
        return "T"

    def __str__(self):
        return "T"