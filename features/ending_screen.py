from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

class EndingScreen(qtw.QDialog):
    """
    EndingScreen class to display the game result and options to restart or exit.
    """
    
    result_messages = {
        "white": ("You Win!", "Congratulations 🎉", "#00ff00"),
        "black": ("You Lose", "Uh oh.", "#ff0000"),
        "stalemate": ("Stalemate", "It's a draw.", "#0000ff"),
        "time out": ("Time's Up!", "That is bad.", "#ffa500"),}
    X_offset = 10
    Y_offset = 50
    
    def __init__(self, winner: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Over!")
        self.setModal(True)
        
        
        self.setStyleSheet("padding: 5px 40px 5px 40px;")
        
        layout = qtw.QVBoxLayout(self)
        
        title, message, color = self.result_messages.get(winner, ("Game Over", "No winner", "black"))
        self.color = qtg.QColor(color)
        
        result_lbl = qtw.QLabel(title, self)
        result_lbl.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        result_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.color.darker(150).name()};")
        layout.addWidget(result_lbl)
        
        subtitle_lbl = qtw.QLabel(message, self)
        subtitle_lbl.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        subtitle_lbl.setStyleSheet(f"font-size: 18px;")
        layout.addWidget(subtitle_lbl)
    
    def paintEvent(self, event: qtg.QPaintEvent):
        painter = qtg.QPainter(self)
        gradient = qtg.QLinearGradient(-self.X_offset, -self.Y_offset, self.width() + self.X_offset, self.height() + self.Y_offset)
        gradient.setColorAt(0, qtg.QColor("#c6c6c6"))
        gradient.setColorAt(1, qtg.QColor(self.color))
        painter.fillRect(self.rect(), gradient)
        
if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    dialog = EndingScreen("Stalemate")
    dialog.exec()
    sys.exit(app.exec())