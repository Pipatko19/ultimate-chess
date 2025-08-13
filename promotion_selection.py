from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt
from piece_view import SPRITE_PATHS
import piece_model

class PromotionSelection(qtw.QDialog):
    """
    PromotionSelection class to allow the player to choose a piece for pawn promotion.
    """
    
    def __init__(self, color: str, parent=None, square_size=50):
        super().__init__(parent)
        self.setWindowTitle("Promote Pawn")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True) 
        self.setStyleSheet("""
            QDialog {
                border: 3px solid #4A90E2;       /* blue border */
            }
        """)
        
        layout = qtw.QHBoxLayout(self)
        
        self.piece_buttons = {}
        pieces = [piece_model.Knight, piece_model.Rook, piece_model.Bishop, piece_model.Queen]
        
        
        for piece in pieces:
            button = qtw.QPushButton(self)
            
            button.setFixedSize(square_size, square_size)
            button.setIcon(qtg.QIcon(SPRITE_PATHS[piece].format(color=color)))
            button.setIconSize(qtc.QSize(square_size, square_size))
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    }
                QPushButton:hover {
                    background-color: #dfdf88;
                    }             """)
            
            button.clicked.connect(lambda _, p=piece: self.select_piece(p(color=color)))
            layout.addWidget(button)
            self.piece_buttons[piece] = button
        
        self.selected_piece = None

    def select_piece(self, piece: piece_model.ChessPiece) -> None:
        """Set the selected piece and close the dialog."""
        self.selected_piece = piece
        print(self.selected_piece)
        self.accept()  # Close the dialog and signal that a piece has been selected


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    dialog = PromotionSelection("white")
    if dialog.exec() == qtw.QDialog.DialogCode.Accepted:
        print(f"Selected piece: {dialog.selected_piece}")
    else:
        print("Dialog was cancelled.")
    sys.exit(app.exec())