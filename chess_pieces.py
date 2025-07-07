from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt
from abc import ABC, abstractmethod, ABCMeta

class MetaQObjectABC(type(qtw.QGraphicsPixmapItem), ABCMeta): #type: ignore
    pass

class ChessPiece(qtw.QGraphicsPixmapItem, metaclass=MetaQObjectABC):
    def __init__(self, color, square_size: int, parent=None):
        super().__init__(parent)
        self.square_size = square_size  # Placeholder for square size, will be set later
        self.color = color
        self.row = 0
        self.col = 0
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
    
    def _set_pixmap(self, path: str):
        pixmap = qtg.QPixmap(path)
        new_pixmap = pixmap.scaled(self.square_size, self.square_size, Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(new_pixmap)
        
    @abstractmethod
    def get_valid_moves(self, board_state) -> list[tuple[int, int]]:
        """
        Abstract method to get valid moves for the piece.
        :param board_state: The current state of the chessboard.
        :return: A list of valid moves.
        """
        pass
    
    def set_square_size(self, size: int):
        self.square_size = size

    def update_pos(self, row: int, col: int):
        self.row = row
        self.col = col
        self.setPos(col * self.square_size, row * self.square_size)
    
    def mouseMoveEvent(self, event):
        # Calculate the new position snapped to grid
        pos = event.scenePos()  # current mouse position in scene coordinates
        x = round((pos.x() - self.square_size // 2 ) / self.square_size) * self.square_size
        y = round((pos.y() - self.square_size // 2 ) / self.square_size) * self.square_size

        # Move the item to the snapped position
        self.setPos(qtc.QPointF(x, y))

        # Accept the event to prevent default handling
        event.accept()

class TestPiece(ChessPiece):
    def __init__(self, color, square_size: int, parent=None):
        super().__init__(color, square_size, parent)
        self._set_pixmap(f"images/pawn.png") 
        print(self.pixmap(), self.pixmap().size())

    def get_valid_moves(self, board_state):
        # Placeholder implementation for valid moves
        return [(self.row + 1, self.col), (self.row - 1, self.col)]