from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt

import piece_model

SPRITE_PATHS = {
    piece_model.Knight: "images/{color}/knight.png",
    piece_model.Rook: "images/{color}/rook.png",
    piece_model.Bishop: "images/{color}/bishop.png",
    piece_model.Queen: "images/{color}/queen.png",
    piece_model.Pawn: "images/{color}/pawn.png",
    piece_model.King: "images/{color}/king.png",
    piece_model.TestPiece: "images/{color}/test.png"
}

def set_pixmap(piece: piece_model.ChessPiece, square_size: int) -> qtg.QPixmap:
    """
    Returns a QPixmap for the given piece and square size.
    """
    sprite_path = SPRITE_PATHS.get(piece.__class__, "images/{color}/default.png")
    pixmap = qtg.QPixmap(sprite_path.format(color=piece.color))
    return pixmap.scaled(square_size, square_size, Qt.AspectRatioMode.IgnoreAspectRatio)


class ChessSignals(qtc.QObject):
    """
    Signals for chess pieces.
    This class is used to define signals that can be emitted by chess pieces.
    """
    pieceClicked = qtc.Signal(int, int)  # Signal emitted when a piece is clicked, with row and column as parameters
    pieceMoved = qtc.Signal(int, int, int, int)  # Signal emitted when a piece is moved, with old row, old col, new row, and new col as parameters

class PieceView(qtw.QGraphicsPixmapItem):
    def __init__(self, square_size:int, piece: piece_model.ChessPiece):
        super().__init__()
        self.square_size = square_size
        
        self.signals = ChessSignals()
        self.color = piece.color
        self.col = 0
        self.row = 0
        
        self.setZValue(1)

        
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        self.set_pixmap(piece, square_size)

    def set_pixmap(self, piece: piece_model.ChessPiece, square_size: int):
        """
        Returns a QPixmap for the given piece and square size.
        """
        sprite_path = SPRITE_PATHS.get(piece.__class__, "images/{color}/test.png")
        pixmap = qtg.QPixmap(sprite_path.format(color=piece.color))
        scaled_pixmap = pixmap.scaled(square_size, square_size, Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(scaled_pixmap)
    
    def reset_pos(self):
        """Return the piece back to its previous position."""
        self.visual_update(self.col, self.row)
    
    def visual_update(self, col: int, row: int):
        """Updates the visual position of the piece on the board."""
        self.col = col
        self.row = row
        self.setPos(self.col * self.square_size, self.row * self.square_size)
        
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
        
        col = round((pos.x() - self.square_size // 2 ) / self.square_size)
        row = round((pos.y() - self.square_size // 2 ) / self.square_size)
        print("POSITION", col, row)
        
        self.setZValue(1)
        # Accept the event to prevent default handling
        self.signals.pieceMoved.emit(prev_col, prev_row, col, row)
        
        event.accept()
