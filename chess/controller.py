from PySide6 import QtCore as qtc, QtWidgets as qtw

from board_initializer import BOARD, board_parser

from chess.MoveTypes import Move, MoveEffect
from chess.GameState import GameState
from chess.piece_view import PieceView
from chess.visual_manager import VisualManager

from features.audio_master import AudioMaster

class GameController(qtc.QObject):
    """
    GameMaster class to manage the chess game logic.
    It handles the game state, player turns, and interactions with the chessboard.
    """
    second_passed = qtc.Signal()
    moved = qtc.Signal(Move, str)
    
    def __init__(self, scene: qtw.QGraphicsScene, square_size: int = 50):
        super().__init__()

        
        self.game_state = GameState()
        self.visual = VisualManager(square_size, scene)
        
        self.visual.clicked.connect(self.on_piece_clicked)
        self.visual.released.connect(self.on_piece_released)
        
        self.board_view: dict[tuple[int, int], PieceView] = {}

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
    
    def start_game(self, board=BOARD):
        board = board_parser(board)
        self.game_state.start(board)
        self.visual.start(board)
        print("Game started. White's turn.")
    
    @qtc.Slot(int, int)
    def on_piece_clicked(self, col: int, row: int):
        self.visual.highlight_possible(self.game_state.generate_moves(col, row))
            
    @qtc.Slot(int, int, int, int)
    def on_piece_released(self, from_col: int, from_row: int, to_col: int, to_row: int):
        self.audio_master.play_place_effect()


        move_container = self.game_state.evaluate_move(from_col, from_row, to_col, to_row)

        if move_container is None:
            print("RESETIING!")
            self.visual.reset_pos(from_col, from_row)
            return
        self.visual.highlight_previous(to_col, to_row)
        
        move, move_effect = move_container
        
        self.game_state.update_board(move_effect) #update model
        self._update_turn(move_effect) #update view

        self.send_move_data(move) #update history


        self.game_state.switch_turn()
        

    def _update_turn(self, move_effect: MoveEffect):
        if (target := move_effect.captured):
            self.visual.remove_piece(*target)
        for from_pos, to_pos in move_effect.moved_pieces:
            self.visual.move_piece(*from_pos, *to_pos)
            if move_effect.promotion:
                self.audio_master.play_promotion_effect()
                color = move_effect.promotion
                selected_piece = self.visual.show_promotion_screen(color)
                
                self.visual.change_piece(*to_pos, selected_piece)
                self.game_state.on_promotion(*to_pos, selected_piece)
        if move_effect.checkmate or move_effect.stalemate:
            if move_effect.checkmate:
                self.audio_master.play_fanfare_effect()
                winner = self.game_state.current_turn
            else:
                winner = "stalemate"
            self.end(winner)


    def end(self, message: str):
        self.remaining_time.stop()
        self.visual.show_ending_screen(message)
        
