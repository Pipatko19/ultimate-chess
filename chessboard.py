from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt

class Chessboard(qtw.QGraphicsItem):
    def __init__(self, length: int, width: int, square_size = 50, parent=None):
        super().__init__(parent)
        self.length = length
        self.width = width
        self.square_size = square_size
        self.border_size = square_size // 25
        
        self.selected_squares: set[tuple[int, int]] = set()
        self.prev_square: tuple[int, int] | None = None
    
    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.length * self.square_size + 1, self.width * self.square_size + 1)

    def paint(self, painter:qtg.QPainter, option:qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget | None = None):
        colors = [qtg.QColor("white"), qtg.QColor("red")]
        
        resized_rect = lambda col, row: qtc.QRectF(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
        
        for row in range(self.width):
            for col in range(self.length):
                color = colors[(row + col) % len(colors)]
                painter.setBrush(color)
                painter.setPen(qtg.QPen(qtg.QColor("black"), self.border_size))
                rect = resized_rect(col, row)
                painter.drawRect(rect)

        if self.prev_square:
            col, row = self.prev_square
            grayed_rect = resized_rect(col, row)
            painter.setBrush(qtg.QColor(102, 153, 153))
            painter.drawRect(grayed_rect)

        for square in self.selected_squares:
            col, row = square
            highlight_rect = resized_rect(col, row)
            painter.setPen(qtg.QPen(qtg.QColor(255, 255, 100), 2))
            painter.setBrush(qtg.QColor(255, 255, 100, 40))
            painter.drawRect(highlight_rect)
        
    def highlight_square(self, col: int, row: int):
        self.selected_squares.add((col, row))
        self.update()
    
    def update_highlighted(self, new_col: int, new_row: int):
        print("UNHIGHLIGHTING")
        self.selected_squares = set()
        self.prev_square = (new_col, new_row)
        self.update()



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