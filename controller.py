from PySide6 import QtCore as qtc, QtWidgets as qtw
from PySide6.QtCore import Qt

from chessboard import Chessboard
from board_initializer import BOARD, TEST_BOARD, board_parser
from board import Board
from move_generator import MoveGenerator, find_move
from piece_view import PieceView

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
        
        self.board_view: dict[tuple[int, int], PieceView] = {}
        self.board_model = Board()
        
        self.move_generator = MoveGenerator(self.board_model)
        self.game_over = False
        self.in_check = False

        self.current_turn = "white"  # Start with white's turn
        self._valid_moves = list()
        

    def switch_turn(self):
        """Switch the turn between players."""
        if not self.game_over:
            self.current_turn = "black" if self.current_turn == "white" else "white"
            print(f"It's now {self.current_turn}'s turn.")
            
    def start_game(self, board = BOARD):
        """Initialize the game state."""
        self.current_turn = "white"
        classed_board = board_parser(board)
        
        for row in range(8):
            for col in range(8):
                piece_model = classed_board[row][col]
                if piece_model is None:
                    continue
                
                #data config
                self.board_model.place_piece(piece_model, col, row)
                
                #view config
                piece_view = PieceView(self.square_size, piece_model)
                self.board_view[(col, row)] = piece_view
                self.scene.addItem(piece_view)
                piece_view.visual_update(col, row)
                
                #doesn't work without the lambda for some internal pyside6 reason
                piece_view.signals.pieceClicked.connect(lambda r, c: self.on_piece_clicked(r, c)) 
                piece_view.signals.pieceMoved.connect(self.on_piece_released)
                
        print("Game started. White's turn.")
        print(self.board_model)
        
    @qtc.Slot(int, int)
    def on_piece_clicked(self, col: int, row: int):
        self.chessboard.highlight_square(col, row)
        piece = self.board_model.get_piece(col, row)
        
        if piece is None:
            return
        
        self._valid_moves = self.move_generator.generate_moves(piece, col, row)
        for move in self._valid_moves:
            self.chessboard.highlight_square(move["to_col"], move["to_row"])
            

    @qtc.Slot(int, int, int, int)
    def on_piece_released(self, from_col: int, from_row: int, to_col: int, to_row: int):
        piece = self.board_model.get_piece(from_col, from_row)
        self.chessboard.update_highlighted(to_col, to_row)
        if piece is None:
            print("NON")
            return

        move = find_move(self._valid_moves, to_col, to_row)
        
        if move is None:
            print("THIS IS NOT VALID MOVE", from_col, from_row, to_col, to_row)
            self.board_view[(from_col, from_row)].reset_pos()
            return
        


        
        self.handle_move(from_col, from_row, to_col, to_row)
        match move["type"]:
            case "capture":
                self.scene.removeItem(self.board_view[(to_col, to_row)])
            case "castle":
                rook_start_col = 0 if from_col > to_col else 7
                rook_end_col = 3 if from_col > to_col else 5
                self.handle_move(rook_start_col, from_row, rook_end_col, from_row)
            
        print("CHECK?:", self.move_generator.in_check("black"))
        
        self._valid_moves.clear()
        # self.handle_check()
        

            
        print(self.board_model)
    
    def handle_move(self, from_col, from_row, to_col, to_row):

        self.board_model.move_piece(from_col, from_row, to_col, to_row)
        # 2. Update the View (using the map)
        piece_view = self.board_view[(from_col, from_row)]
        piece_view.visual_update(to_col, to_row)

        # 3. Update the controller's view map to reflect the new position
        self.board_view[(to_col, to_row)] = self.board_view.pop((from_col, from_row))
