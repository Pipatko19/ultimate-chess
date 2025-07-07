from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt

from chess_pieces import TestPiece, ChessPiece
from chessboard import Chessboard

class GameController:
    """
    GameMaster class to manage the chess game logic.
    It handles the game state, player turns, and interactions with the chessboard.
    """
    
    def __init__(self, scene: qtw.QGraphicsScene, square_size: int = 50):
        self.square_size = square_size
        self.scene = scene
        self.current_turn = "white"  # Start with white's turn
        self.board: list[list[ChessPiece | None]] = [[None for _ in range(8)] for _ in range(8)]
        self.game_over = False

    def switch_turn(self):
        """Switch the turn between players."""
        if not self.game_over:
            self.current_turn = "black" if self.current_turn == "white" else "white"
            print(f"It's now {self.current_turn}'s turn.")
    def move_piece(self, piece: ChessPiece, new_row: int, new_col: int):
        piece.update_pos(new_row, new_col)
    
    def start_game(self):
        """Initialize the game state."""
        self.game_over = False
        self.current_turn = "white"
        self.board = [[None for _ in range(8)] for _ in range(8)]
        
        for col in range(8):
            piece = TestPiece("white", self.square_size)
            self.board[0][col] = piece
            self.scene.addItem(piece)
            piece.setZValue(1)
        
        print("Game started. White's turn.")