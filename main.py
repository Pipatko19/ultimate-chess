from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

from chess.controller import GameController

from features.time import TimeDisplay
from features.history import HistoryDisplay

SQUARE_SIZE = 75  # Default square size for the chessboard

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Chess")
        self.setGeometry(100, 100, 800, 600)

        central = qtw.QWidget(self)
        main_layout = qtw.QGridLayout(self)
        
        scene = qtw.QGraphicsScene(self)
        controller = GameController(scene, SQUARE_SIZE)
        controller.start_game()
        
        view = qtw.QGraphicsView(scene, self)
        view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)
        view.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)
        view.setMinimumSize(8 * SQUARE_SIZE + 5, 8 * SQUARE_SIZE + 5)
        
        time_display = TimeDisplay(self)
        
        controller.second_passed.connect(time_display.update_time)
        time_display.timer_ended.connect(lambda: controller.end("time out"))
        
        history_display = HistoryDisplay(self)
        history_display.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)
        
        controller.moved.connect(history_display.add_move)
        
        # Create a central widget
        main_layout.addWidget(time_display, 0, 0, 1, 2)
        main_layout.addWidget(view, 1, 0)
        main_layout.addWidget(history_display, 1, 1)
        
        main_layout.setRowStretch(1, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        central.setLayout(main_layout)
        self.setCentralWidget(central)
        

        


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())