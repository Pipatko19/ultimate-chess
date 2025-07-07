from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt

from chess_pieces import ChessPiece

class Chessboard(qtw.QGraphicsItem):
    def __init__(self, length: int, width: int, square_size = 50, parent=None):
        super().__init__(parent)
        self.length = length
        self.width = width
        self.square_size = square_size
        
        self.border_size = square_size // 25
        self.selected_square: tuple[int, int] | None = None
    
    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.length * self.square_size + 1, self.width * self.square_size + 1)

    def paint(self, painter:qtg.QPainter, option:qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget | None = None):
        colors = [qtg.QColor("white"), qtg.QColor("gray")]
        
        for row in range(self.width):
            for col in range(self.length):
                color = colors[(row + col) % 2]
                painter.setBrush(color)
                painter.setPen(qtg.QPen(qtg.QColor("black"), self.border_size))
                rect = qtc.QRectF(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                painter.drawRect(rect)
        
        if self.selected_square is not None:
            col, row = self.selected_square
            highlight_rect = qtc.QRectF(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
            painter.setPen(qtg.QPen(qtg.QColor("red"), 2))
            painter.setBrush(qtg.QColor(255, 255, 100))  # Semi-transparent yellow
            painter.drawRect(highlight_rect)
                
    def mousePressEvent(self, event: qtw.QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            col = int(event.pos().x() // self.square_size)
            row = int(event.pos().y() // self.square_size)
            self.selected_square = (col, row)
            print(f"Clicked on square at ({self.selected_square})")
            self.update()

        super().mousePressEvent(event)


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    chessboard = Chessboard(8, 8, 50)
    scene = qtw.QGraphicsScene()
    scene.addItem(chessboard)
    
    view = qtw.QGraphicsView(scene)
    view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)
    view.setWindowTitle("Chessboard")
    view.resize(400, 400)
    view.show()
    
    sys.exit(app.exec())