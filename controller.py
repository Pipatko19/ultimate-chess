from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt

from chess_pieces import TestPiece, ChessPiece, King
from chessboard import Chessboard
from board_initializer import board_parser, BOARD, TEST_BOARD

class GameController(qtc.QObject):
    """
    GameMaster class to manage the chess game logic.
    It handles the game state, player turns, and interactions with the chessboard.
    """
    
    def __init__(self, scene: qtw.QGraphicsScene, chessboard: Chessboard, square_size: int = 50):
        super().__init__()
        self.square_size = square_size
        self.scene = scene
        self.chessboard = chessboard
        self.current_turn = "white"  # Start with white's turn
        self.board: list[list[ChessPiece | None]] = []
        self.game_over = False

    def switch_turn(self):
        """Switch the turn between players."""
        if not self.game_over:
            self.current_turn = "black" if self.current_turn == "white" else "white"
            print(f"It's now {self.current_turn}'s turn.")
            
    def get_piece_at(self, col: int, row: int) -> ChessPiece | None:
        piece = self.board[row][col]
        return piece

    def start_game(self):
        """Initialize the game state."""
        self.current_turn = "white"
        self.board = board_parser(BOARD)
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    continue
                
                self.scene.addItem(piece)
                #piece.set_board_state(self.board)
                piece.set_square_size(self.square_size)
                piece.update_pos(starting=True)
                
                #doesn't work without the lambda for some internal pyside6 reason
                piece.signals.pieceClicked.connect(lambda r, c: self.on_piece_clicked(r, c)) 
                piece.signals.pieceMoved.connect(self.on_piece_released)
                
        print("Game started. White's turn.")
    
    @qtc.Slot(int, int)
    def on_piece_clicked(self, col: int, row: int):
        self.chessboard.highlight_square(col, row)
        piece = self.get_piece_at(col, row)
        if piece is not None:
            for move_col, move_row in piece.get_valid_moves():
                self.chessboard.highlight_square(move_col, move_row)
    
    @qtc.Slot(int, int, int, int)
    def on_piece_released(self, prev_col: int, prev_row: int, new_col: int, new_row: int):
        piece = self.get_piece_at(prev_col, prev_row)
        self.chessboard.update_highlighted(new_col, new_row)
        if piece is None:
            print("NON")
            return

        valid_moves = piece.get_valid_moves()
        
        if (new_col, new_row) not in valid_moves:
            print("MOVES", valid_moves)
            print("THIS IS NOT VALID MOVE", prev_col, prev_row, new_col, new_row)
            piece.visual_update()
            return
        
        if isinstance(piece, King):
            castle_move = piece.castles_valid()
            if castle_move:
                piece.castle(new_col)
                return
        
        print("VALID MOVE, UPDATING")

        if (captured_piece:=self.board[new_row][new_col]) is not None:
            print("CAPTURED PIECE", captured_piece)
            self.scene.removeItem(captured_piece)
        self.board[prev_row][prev_col] = None
        self.board[new_row][new_col] = piece
        piece.update_pos()

            
        print(*(" ".join(str(piece) if piece is not None else "*" for piece in row) for row in self.board), sep="\n")
        print("\n")
