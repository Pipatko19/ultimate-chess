from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

from chess.piece_model import ChessPiece
from chess.piece_view import PieceView
from chess.chessboard import Chessboard

from features.promotion_selection import PromotionSelection
from features.ending_screen import EndingScreen

from chess.MoveTypes import Move

class VisualManager(qtc.QObject):
    clicked = qtc.Signal(int, int)
    released = qtc.Signal(int, int, int, int)
    
    
    def __init__(self, square_size: int, scene: qtw.QGraphicsScene):
        super().__init__()
        self.square_size = square_size
        self.scene = scene
        self.pieces: dict[tuple[int, int], PieceView] = {}
        
    
    def _start_board(self):
        self.board = Chessboard(8, 8, self.square_size)
        self.scene.addItem(self.board)
        self.board.play_wave_animation()
        
    def start(self, board: list[list[ChessPiece | None]]):    
        self._start_board()
        for row in range(len(board)):
            for col in range(len(board[0])):
                piece = board[row][col]
                if piece is None:
                    continue
                piece_view = PieceView(self.square_size, piece)
                self.pieces[(col, row)] = piece_view
                self.scene.addItem(piece_view)
                piece_view.visual_update(col, row)
                
                piece_view.signals.pieceClicked.connect(self.on_clicked) #hmmm
                piece_view.signals.pieceMoved.connect(self.on_piece_released)
    
    @qtc.Slot(int, int)
    def on_clicked(self, row: int, col: int):
        self.clicked.emit(row, col)

    def highlight_possible(self, moves: list[Move]):
        for move in moves:
            self.board.highlight_square(move["to_col"], move["to_row"])
    
    def highlight_previous(self, col: int, row: int):
        self.board.highlight_previous(col, row)

    def reset_pos(self, col: int, row: int):
        if (col, row) in self.pieces:
            self.pieces[(col, row)].reset_pos()
        else:
            raise ValueError("Position not found in piece views dictionary")
    
    def remove_piece(self, col: int, row: int):
        if (col, row) in self.pieces:
            self.scene.removeItem(self.pieces.pop((col, row)))
        else:
            raise ValueError("Position not found in piece views dictionary")

    @qtc.Slot(int, int, int, int)
    def on_piece_released(self, from_col: int, from_row: int, to_col: int, to_row: int):
        self.board.reset_highlight()
        
        self.released.emit(from_col, from_row, to_col, to_row)


    def move_piece(self, from_col: int, from_row: int, to_col: int, to_row: int):
        
        # 1. Update the View (using the map)
        piece = self.pieces[(from_col, from_row)]
        piece.visual_update(to_col, to_row)

        # 2. Update the visual manager's view map to reflect the new position
        self.pieces[(to_col, to_row)] = self.pieces.pop((from_col, from_row))
    
    def change_piece(self, col: int, row: int, new_piece: ChessPiece):
        self.pieces[(col, row)].set_pixmap(new_piece, self.square_size)

    
    def show_promotion_screen(self, color: str) -> ChessPiece:
        dialog = PromotionSelection(color, parent=self.scene.views()[0])
        if dialog.exec() == qtw.QDialog.DialogCode.Accepted and dialog.selected_piece:
            return dialog.selected_piece
        else:
            raise ValueError("No piece selected")
    
    def show_ending_screen(self, winner: str) -> None:
        ending_screen = EndingScreen(winner, parent=self.scene.views()[0])
        ending_screen.exec()