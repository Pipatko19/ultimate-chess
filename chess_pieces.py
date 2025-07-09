from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt
from abc import abstractmethod, ABCMeta

class MetaQObjectABC(type(qtw.QGraphicsPixmapItem), ABCMeta): #type: ignore
    pass

class ChessSignals(qtc.QObject):
    """
    Signals for chess pieces.
    This class is used to define signals that can be emitted by chess pieces.
    """
    pieceClicked = qtc.Signal(int, int)  # Signal emitted when a piece is clicked, with row and column as parameters
    pieceMoved = qtc.Signal(int, int, int, int)  # Signal emitted when a piece is moved, with old row, old col, new row, and new col as parameters

class ChessPiece(qtw.QGraphicsPixmapItem, metaclass=MetaQObjectABC):
    @abstractmethod
    def get_valid_moves(self, board_state: list[list["ChessPiece | None"]]) -> set[tuple[int, int]]:
        """
        Abstract method to get valid moves for the piece.
        :param board_state: The current state of the chessboard.
        :return: A list of valid moves.
        """ 
        pass
    
    def __init__(self, color, square_size: int, parent=None):
        super().__init__(parent)
        self.signals = ChessSignals()
        self.square_size = square_size 
        self.color = color
        self.row = 0
        self.col = 0
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        self.setZValue(1)
        
    
    def _set_pixmap(self, path: str):
        pixmap = qtg.QPixmap(path)
        new_pixmap = pixmap.scaled(self.square_size, self.square_size, Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(new_pixmap)
    
    def set_square_size(self, size: int):
        self.square_size = size

    def update_pos(self, col: int, row: int):
        print("UPDATING POS", col, row)
        self.row = row
        self.col = col
        self.setPos(col * self.square_size, row * self.square_size)

    def boundingRect(self) -> qtc.QRectF:
        return qtc.QRectF(0, 0, self.square_size, self.square_size)

    def shape(self) -> qtg.QPainterPath:
        path = qtg.QPainterPath()
        path.addRect(0, 0, self.square_size, self.square_size)
        return path
    
    def mousePressEvent(self, event: qtw.QGraphicsSceneMouseEvent):
        self.setZValue(2)
        self.signals.pieceClicked.emit(self.col, self.row)

    def mouseMoveEvent(self, event: qtw.QGraphicsSceneMouseEvent):
        pos = event.scenePos()
        x = round(pos.x() - self.square_size // 2)
        y = round(pos.y() - self.square_size // 2)
        self.setPos(qtc.QPointF(x, y))
        event.accept()
    
    def mouseReleaseEvent(self, event: qtw.QGraphicsSceneMouseEvent):
        # Calculate the new position snapped to grid
        pos = event.scenePos()  # current mouse position in scene coordinates
        
        prev_row = self.row
        prev_col = self.col
        
        self.col = round((pos.x() - self.square_size // 2 ) / self.square_size)
        self.row = round((pos.y() - self.square_size // 2 ) / self.square_size)
        print("POS", self.col, self.row)
        
        self.setZValue(1)
        # Accept the event to prevent default handling
        self.signals.pieceMoved.emit(prev_col, prev_row, self.col, self.row)
        
        event.accept()

class Rook(ChessPiece):
    def __init__(self, color, square_size: int, parent=None):
        super().__init__(color, square_size, parent)
        self._set_pixmap(f"images/rook.png")

    def get_valid_moves(self, board_state):
        # Placeholder implementation for valid moves
        return {(self.col + i, self.row) for i in range(-7, 8) if i != 0 and 0 <= self.col + i < 8} | \
               {(self.col, self.row + i) for i in range(-7, 8) if i != 0 and 0 <= self.row + i < 8}

    def __repr__(self):
        return "R"

class TestPiece(ChessPiece):
    def __init__(self, color, square_size: int, parent=None):
        super().__init__(color, square_size, parent)
        self._set_pixmap(f"images/pawn.png") 
        print(self.pixmap(), self.pixmap().size())

    def get_valid_moves(self, board_state):
        # Placeholder implementation for valid moves
        return {(self.col + 1, self.row), (self.col - 1, self.row)}

    def __repr__(self):
        return "T"

    def __str__(self):
        return "T"