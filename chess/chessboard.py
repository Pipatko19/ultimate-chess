from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

BOARD_COLORS = [qtg.QColor("#ffd47d"), qtg.QColor("#f2ab1b")]
SQUARE_OUTLINE = qtg.QPen(qtg.QColor("black"), 2)

PREVIOUS_SQUARE_COLOR = qtg.QColor(102, 153, 153)

AVAILABLE_OUTLINE = qtg.QPen(qtg.QColor(255, 255, 100), 2)
AVAILABLE_SQUARE_COLOR = qtg.QColor(255, 255, 100, 40)

class ChessSquare(qtw.QGraphicsObject):
    def __init__(self, square_size: int, color, parent=None):
        super().__init__(parent)
        self.setOpacity(0)
        
        self.base_color = color
        self.highlighted = False
        self.previous = False
        self.rect = qtc.QRectF(0, 0, square_size - 1, square_size - 1) #offset for border
    
    def paint(self, painter: qtg.QPainter, option: qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget | None = None):

        if self.highlighted:
            outline = AVAILABLE_OUTLINE
            color = self.base_color.lighter(110)
        else:
            outline = SQUARE_OUTLINE
            color = self.base_color
            
        if self.previous:
            color = PREVIOUS_SQUARE_COLOR
        
        
        painter.setPen(outline)
        painter.setBrush(color)
        painter.drawRect(self.rect)
        
    def boundingRect(self) -> qtc.QRectF:
        return self.rect

class Chessboard(qtw.QGraphicsObject):
    def __init__(self, length: int, width: int, square_size = 50, parent=None):
        super().__init__(parent)
        self.length = length
        self.width = width
        self.square_size = square_size
        
        self.squares: list[list[ChessSquare]] = []
        for row in range(self.width):
            self.squares.append([])
            for col in range(self.length):
                color = BOARD_COLORS[(row + col) % len(BOARD_COLORS)]
                square = ChessSquare(square_size, color)
                square.setParentItem(self)
                square.setPos(col * square_size, row * square_size)
                self.squares[row].append(square)
                
        self.prev_square: ChessSquare | None = None
        


    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.length * self.square_size + 1, self.width * self.square_size + 1)

    def paint(self, painter: qtg.QPainter, option: qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget | None = None):
        pass

    def highlight_square(self, col: int, row: int):
        self.squares[row][col].highlighted = True
        self.update()

    def reset_highlight(self):
        for row in range(self.width):
            for col in range(self.length):
                self.squares[row][col].highlighted = False
        self.update()
    
    def highlight_previous(self, new_col: int, new_row: int):
        if self.prev_square:
            self.prev_square.previous = False
        
        self.prev_square = self.squares[new_row][new_col]
        self.prev_square.previous = True
        self.update()
    
    def play_wave_animation(self):
        print("play")
        master_animation = qtc.QParallelAnimationGroup(self)
        
        STAGGER_DELAY = 100
        DURATION = 700
        
        for row in range(self.width):
            for col in range(self.length):
                square = self.squares[row][col]
                
                delay = STAGGER_DELAY * (row + col)
                
                compounded_animation = qtc.QSequentialAnimationGroup(square)
                compounded_animation.addPause(delay)
                
                animation = qtc.QParallelAnimationGroup(square)
                
                translate_animation = qtc.QPropertyAnimation(square, b"pos")
                translate_animation.setDuration(DURATION)
                translate_animation.setStartValue(square.pos() - qtc.QPointF(0, 50))
                translate_animation.setEndValue(square.pos())
                
                fadein_animation = qtc.QPropertyAnimation(square, b"opacity")
                fadein_animation.setDuration(DURATION)
                fadein_animation.setStartValue(0)
                fadein_animation.setEndValue(1)
                
                animation.addAnimation(translate_animation)
                animation.addAnimation(fadein_animation)
                compounded_animation.addAnimation(animation)
                master_animation.addAnimation(compounded_animation)

        master_animation.start()

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
    
    shortcut = qtg.QShortcut(qtg.QKeySequence("W"), view)
    shortcut.activated.connect(chessboard.play_wave_animation)
    
    sys.exit(app.exec())