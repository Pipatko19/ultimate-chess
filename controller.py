from PySide6 import QtCore as qtc, QtWidgets as qtw

from chessboard import Chessboard
from board_initializer import BOARD, TEST_BOARD, board_parser
from board import Board
from piece_model import ChessPiece
from move_generator import MoveGenerator, find_move, MoveType
from piece_view import PieceView
from ending_screen import EndingScreen
from promotion_selection import PromotionSelection

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
        self.in_check = False

        self.current_turn = "white"  # Start with white's turn
        self._valid_moves = list()
        

    def switch_turn(self):
        """Switch the turn between players."""
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
        
        if piece is None or piece.color != self.current_turn:
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
        
        move_type = move["type"]

        print("MOVE", move)

        
        if MoveType.CAPTURE & move_type: 
            self.scene.removeItem(self.board_view[(to_col, to_row)])
        if MoveType.NORMAL & move_type:
            self.handle_move(from_col, from_row, to_col, to_row)
        if MoveType.CASTLE & move_type:
            rook_start_col = 0 if from_col > to_col else 7
            rook_end_col = 3 if from_col > to_col else 5
            self.handle_move(rook_start_col, from_row, rook_end_col, from_row)
        if MoveType.PROMOTION & move_type:
            dialog = PromotionSelection(piece.color, parent=self.scene.views()[0])
            if dialog.exec() == qtw.QDialog.DialogCode.Accepted and dialog.selected_piece:
                self.promote_pawn(to_col, to_row, dialog.selected_piece)
        if MoveType.DOUBLE_PAWN_MOVE & move_type:
            self.move_generator.set_en_passant(to_col, to_row, piece.color)
        else:
            self.move_generator.reset_en_passant()
        if MoveType.EN_PASSANT & move_type:
            removed_row = to_row + (1 if piece.color == "white" else -1)
            self.scene.removeItem(self.board_view[to_col, removed_row])
            self.board_model.board[removed_row][to_col] = None
        
        
        self._valid_moves.clear()
        
        winner = None
        if self.is_checkmate("white"):
            winner = "Black"
        elif self.is_checkmate("black"):
            winner = "White"
        if winner:
            print(f"{winner} wins!")
            ending_screen = EndingScreen(winner, parent=self.scene.views()[0])
            if ending_screen.exec():
                self.start_game(TEST_BOARD)

        print(self.board_model)

        self.switch_turn()
    
    def promote_pawn(self, col: int, row: int, piece: ChessPiece):
        """promote a pawn to a new piece type."""
        self.board_view[(col, row)].set_pixmap(piece, self.square_size)
        self.board_model.place_piece(piece, col, row)
        
        
        
    def handle_move(self, from_col, from_row, to_col, to_row):

        self.board_model.move_piece(from_col, from_row, to_col, to_row)
        # 2. Update the View (using the map)
        piece_view = self.board_view[(from_col, from_row)]
        piece_view.visual_update(to_col, to_row)

        # 3. Update the controller's view map to reflect the new position
        self.board_view[(to_col, to_row)] = self.board_view.pop((from_col, from_row))

    def is_checkmate(self, color: str) -> bool:
        """Check if the current player is in checkmate."""
        king_col, king_row = self.board_model.find_king_position(color)
        total_checks, blocking_squares = self.move_generator.in_check(color, king_col, king_row)
        
        if total_checks == 0:
            return False
        
        king = self.board_model.get_piece(king_col, king_row)
        if any(self.move_generator.generate_moves(king, king_col, king_row)): #type: ignore
            return False
        if total_checks == 1:
            for col, row, piece in self.board_model.yieled_all_pieces(color):
                valid_moves = self.move_generator.generate_moves(piece, col, row)
                if any((move["to_col"], move["to_row"]) in blocking_squares for move in valid_moves):
                    return False
        return True