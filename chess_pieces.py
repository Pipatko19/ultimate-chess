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
    
    sprite_path: str
    
    @abstractmethod
    def get_valid_moves(self, board_state: list[list["ChessPiece | None"]]) -> set[tuple[int, int]]:
        """
        Abstract method to get valid moves for the piece.
        :param board_state: The current state of the chessboard.
        :return: A list of valid moves.
        """ 
        pass
    
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.signals = ChessSignals()
        self.square_size = 1 
        self.color = color
        self.row = 0
        self.col = 0
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        self.setZValue(1)
        
    
    def _set_pixmap(self):
        pixmap = qtg.QPixmap(self.sprite_path.format(color=self.color))
        new_pixmap = pixmap.scaled(self.square_size, self.square_size, Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(new_pixmap)
        print(self.pixmap())
    
    def set_square_size(self, size: int):
        self.square_size = size
        self._set_pixmap()

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
    sprite_path = "images/{color}/rook.png"

    def get_valid_moves(self, board_state):
        # Placeholder implementation for valid moves
        
        return {(self.col + i, self.row) for i in range(-7, 8) if i != 0 and 0 <= self.col + i < 8} | \
               {(self.col, self.row + i) for i in range(-7, 8) if i != 0 and 0 <= self.row + i < 8}

    def __repr__(self):
        return "R"

class Knight(ChessPiece):
    sprite_path = "images/{color}/knight.png"
    
    def get_valid_moves(self, board_state):
        return {}
    def __repr__(self):
        return "N"

class Bishop(ChessPiece):
    sprite_path = "images/{color}/bishop.png"
    
    def get_valid_moves(self, board_state):
        return {}
    def __repr__(self):
        return "B"

class Queen(ChessPiece):
    sprite_path = "images/{color}/queen.png"
    
    def get_valid_moves(self, board_state):
        return {}
    def __repr__(self):
        return "Q"

class King(ChessPiece):    
    sprite_path = "images/{color}/king.png"
    
    def get_valid_moves(self, board_state):
        return {}
    def __repr__(self):
        return "K"

class Pawn(ChessPiece):
    sprite_path = "images/{color}/pawn.png"
    
    def get_valid_moves(self, board_state):
        return {}
    def __repr__(self):
        return "P"


class TestPiece(ChessPiece):
    sprite_path = "images/{color}/test.png"
    
    def __init__(self, color, parent=None):
        super().__init__(color, parent)
        print(self.pixmap(), self.pixmap().size())

    def get_valid_moves(self, board_state):
        # Placeholder implementation for valid moves
        return {(i, j) for i in range(8) for j in range(8)}

    def __repr__(self):
        return "T"

    def __str__(self):
        return "T"