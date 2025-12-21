from PySide6 import QtCore as qtc, QtWidgets as qtw

from board_initializer import BOARD

from chess.chessboard import Chessboard
from chess.move_generator import Move
from chess.piece_model import ChessPiece
from chess.piece_view import PieceView
from chess.GameState import GameState, MoveEffect

from features.ending_screen import EndingScreen
from features.promotion_selection import PromotionSelection
from features.audio_master import AudioMaster

class GameController(qtc.QObject):
    """
    GameMaster class to manage the chess game logic.
    It handles the game state, player turns, and interactions with the chessboard.
    """
    second_passed = qtc.Signal()
    moved = qtc.Signal(Move, str)
    
    def __init__(self, scene: qtw.QGraphicsScene, chessboard: Chessboard, square_size: int = 50):
        super().__init__()
        self.square_size = square_size
        self.scene = scene
        self.chessboard = chessboard
        
        self.game_state = GameState()
        
        self.board_view: dict[tuple[int, int], PieceView] = {}
        # self.board_model = Board()
        
        #self.move_generator = MoveGenerator(self.board_model)

        #self.current_turn = "white"  # Start with white's turn
        #self._valid_moves = list()
        
        self.audio_master = AudioMaster()
        
        self.remaining_time = qtc.QTimer(self)
        self.remaining_time.setInterval(1000)
        self.remaining_time.timeout.connect(self.pass_time)
        self.remaining_time.start()
        
        
    def pass_time(self):
        self.second_passed.emit()
        self.audio_master.play_tick_effect()
    
    def send_move_data(self, move: Move):
        self.moved.emit(move, self.game_state.current_turn)
    
    
    def _start_visual(self):
        board = self.game_state.get_snapshot()
        for row in range(len(board)):
            for col in range(len(board[0])):
                piece = board[row][col]
                if piece is None:
                    continue
                piece_view = PieceView(self.square_size, piece)
                self.board_view[(col, row)] = piece_view
                self.scene.addItem(piece_view)
                piece_view.visual_update(col, row)
                
                piece_view.signals.pieceClicked.connect(lambda r, c: self.on_piece_clicked(r, c)) 
                piece_view.signals.pieceMoved.connect(self.on_piece_released)
    
    def start_game(self):
        self.game_state.start(BOARD)
        self._start_visual()
        print("Game started. White's turn.")
    
    @qtc.Slot(int, int)
    def on_piece_clicked(self, col: int, row: int):
        self.chessboard.highlight_square(col, row)
        
        if not self.game_state.is_selectable(col, row):
            return
        
        for move in self.game_state.generate_moves(col, row):
            self.chessboard.highlight_square(move["to_col"], move["to_row"])
            
    @qtc.Slot(int, int, int, int)
    def on_piece_released(self, from_col: int, from_row: int, to_col: int, to_row: int):
        self.chessboard.reset_highlight(to_col, to_row)

        
        
        move_container = self.game_state.evaluate_move(from_col, from_row, to_col, to_row)

        if move_container is None:
            print("THIS IS NOT VALID MOVE", from_col, from_row, to_col, to_row)
            self.board_view[(from_col, from_row)].reset_pos()
            return
        
        move, move_effect = move_container
        
        self.audio_master.play_place_effect()
        self.send_move_data(move)
        self._update_turn(move_effect)

        self.game_state.switch_turn()

    def _update_turn(self, move_effect: MoveEffect):
        if (target := move_effect.captured):
            self.scene.removeItem(self.board_view[*target])
            self.board_view.pop(target)
        for from_pos, to_pos in move_effect.moved:
            self.handle_move_visual(*from_pos, *to_pos)
            if move_effect.promotion:
                self.audio_master.play_promotion_effect()
                
                dialog = PromotionSelection(move_effect.promotion, parent=self.scene.views()[0])
                if dialog.exec() == qtw.QDialog.DialogCode.Accepted and dialog.selected_piece:
                    self.promote_pawn(*to_pos, dialog.selected_piece)
        if move_effect.checkmate:
            self.audio_master.play_fanfare_effect()
            self.remaining_time.stop()
            
            winner = self.game_state.current_turn
            self.end(winner)
            print(f"{winner} wins!")

        elif move_effect.stalemate:
            self.end("stalemate")
            print("Stalemate!")
            self.remaining_time.stop()
            
            
    def handle_move_visual(self, from_col, from_row, to_col, to_row):
        
        # 1. Update the View (using the map)
        piece_view = self.board_view[(from_col, from_row)]
        piece_view.visual_update(to_col, to_row)

        # 2. Update the controller's view map to reflect the new position
        self.board_view[(to_col, to_row)] = self.board_view.pop((from_col, from_row))
        
    
    def promote_pawn(self, col: int, row: int, piece: ChessPiece):
        """promote a pawn to a new piece type. Will fix it later"""
        self.board_view[(col, row)].set_pixmap(piece, self.square_size)
        self.game_state.on_promotion(piece, col, row)
        


    def end(self, winner: str):
        ending_screen = EndingScreen(winner, parent=self.scene.views()[0])
        if ending_screen.exec():
            self.start_game()