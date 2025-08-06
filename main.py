from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

from chessboard import Chessboard
from controller import GameController

SQUARE_SIZE = 75  # Default square size for the chessboard


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Chess")
        self.setGeometry(100, 100, 800, 600)

        scene = qtw.QGraphicsScene(self)


        board = Chessboard(8, 8, SQUARE_SIZE)
        controller = GameController(scene, board, SQUARE_SIZE)
        controller.start_game()
        scene.addItem(board)
        view = qtw.QGraphicsView(scene, self)
        view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)
        
        # Create a central widget
        self.setCentralWidget(view)


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())