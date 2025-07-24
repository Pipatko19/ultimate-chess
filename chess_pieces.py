from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from PySide6.QtCore import Qt
from abc import abstractmethod, ABCMeta, ABC

class FirstMoveMixin:
    """
    Mixin class to handle the first move logic for chess pieces.
    This can be used to implement special rules for pieces that have a different behavior on their first move.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_move = True
    
    def update_pos(self, **kwargs):
        """Updates the position of the piece based on its coordinates in the board state."""
        starting = kwargs.get('starting', False)
        super().update_pos(**kwargs) #type: ignore
        if not starting:
            self.first_move = False  # After the first move, set first_move to False

class MetaQObjectABC(type(qtw.QGraphicsPixmapItem), ABCMeta): #type: ignore
    pass

class ChessSignals(qtc.QObject):
    """
    Signals for chess pieces.
    This class is used to define signals that can be emitted by chess pieces.
    """
    pieceClicked = qtc.Signal(int, int)  # Signal emitted when a piece is clicked, with row and column as parameters
    pieceMoved = qtc.Signal(int, int, int, int)  # Signal emitted when a piece is moved, with old row, old col, new row, and new col as parameters

class ChessPiece(qtw.QGraphicsPixmapItem, ABC, metaclass=MetaQObjectABC):
    
    sprite_path: str
    
    @abstractmethod
    def get_valid_moves(self) -> set[tuple[int, int]]:
        """
        Abstract method to get valid moves for the piece.
        :return: A list of valid moves.
        """ 
        pass
    
    def __init__(self, color, board_state: list[list["ChessPiece | None"]], parent=None):
        super().__init__(parent)
        self.signals = ChessSignals()
        self.square_size = 1 
        self.color = color
        self.board_state = board_state
        self.row = 0
        self.col = 0
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        self.setZValue(1)
        
    def find_coordinates(self):
        """find the coordinates of itself relative in the board. Searches every space"""
        for row_idx, row in enumerate(self.board_state):
            for col_idx, piece in enumerate(row):
                if piece is self:
                    return col_idx, row_idx
        raise ValueError("Piece not found in board state")
                
    def _set_pixmap(self):
        pixmap = qtg.QPixmap(self.sprite_path.format(color=self.color))
        new_pixmap = pixmap.scaled(self.square_size, self.square_size, Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(new_pixmap)
    
    def set_square_size(self, size: int):
        self.square_size = size
        self._set_pixmap()

    def update_pos(self, **kwargs):
        """Updates the position of the piece based on its coordinates in the board state."""
        self.col, self.row = self.find_coordinates()
        print("UPDATING POS", self.col, self.row)
        self.visual_update()


    def visual_update(self):
        """Updates the visual position of the piece on the board."""
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

class Rook(FirstMoveMixin, ChessPiece):
    sprite_path = "images/{color}/rook.png"

    def get_valid_moves(self):
        valid_moves = set()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

        for dx, dy in directions:
            col, row = self.col + dx, self.row + dy
            while 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col] is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col].color != self.color: #type: ignore
                valid_moves.add((col, row))
                

        return valid_moves
    def __repr__(self):
        return "R"

class Knight(ChessPiece):
    sprite_path = "images/{color}/knight.png"
    
    def get_valid_moves(self):
        moves = {
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        }
        valid_moves = set()
        for dx, dy in moves:
            col, row = self.col + dx, self.row + dy
            if 0 <= col < 8 and 0 <= row < 8:
                piece = self.board_state[row][col]
                if piece is None or piece.color != self.color:
                    valid_moves.add((col, row))
        
        return valid_moves
    def __repr__(self):
        return "N"

class Bishop(ChessPiece):
    sprite_path = "images/{color}/bishop.png"
    
    def get_valid_moves(self):
        valid_moves = set()
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]  # diagonal

        for dx, dy in directions:
            col, row = self.col + dx, self.row + dy
            while 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col] is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col].color != self.color: #type: ignore
                valid_moves.add((col, row))
        return valid_moves
    def __repr__(self):
        return "B"

class Queen(ChessPiece):
    sprite_path = "images/{color}/queen.png"
    
    def get_valid_moves(self):
        valid_moves = set()
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # horizontal and vertical
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # diagonal
        ]
        for dx, dy in directions:
            col, row = self.col + dx, self.row + dy
            while 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col] is None:
                valid_moves.add((col, row))
                col += dx
                row += dy
            if 0 <= col < 8 and 0 <= row < 8 and self.board_state[row][col].color != self.color: #type: ignore
                valid_moves.add((col, row))
        return valid_moves
    def __repr__(self):
        return "Q"

class King(FirstMoveMixin, ChessPiece):    
    sprite_path = "images/{color}/king.png"
    
    def castles_valid(self) -> set[tuple[int, int]]:
        valid_castles = set()
        if not self.first_move:
            return valid_castles
        row = self.row
        col = self.col
        
        # King-side castle (short)
        kingside_rook = self.board_state[row][col + 3]
        if isinstance(kingside_rook, Rook) and kingside_rook.first_move:
            if self.board_state[row][col + 1] is None \
                and self.board_state[row][col + 2] is None:
                valid_castles.add((col + 2, row))
        
        # Queen-side castle (long)
        queenside_rook = self.board_state[row][col - 4] if col - 4 >= 0 else None
        if isinstance(queenside_rook, Rook) and queenside_rook.first_move:
            if self.board_state[row][col - 1] is None \
                and self.board_state[row][col - 2] is None \
                and self.board_state[row][col - 3] is None:
                valid_castles.add((col - 2, row))
        return valid_castles
    
    def castle(self, target_col: int):
        row = self.row
        col = self.col

        # Kingside castle
        if target_col == col + 2:
            rook_col = col + 3
            rook = self.board_state[row][rook_col]
            self.board_state[row][col + 1] = rook
            self.board_state[row][rook_col] = None

        # Queenside castle
        elif target_col == col - 2:
            rook_col = col - 4
            rook = self.board_state[row][rook_col]
            self.board_state[row][col - 1] = rook
            self.board_state[row][rook_col] = None

        else:
            return False  # not a castling move

        # Move the king
        self.board_state[row][target_col] = self
        self.board_state[row][col] = None

        rook.update_pos()
        self.update_pos()
        return True

    
    def get_valid_moves(self):
        valid_moves = set()
        moves = [
            (1, 0), (-1, 0), (0, 1),
            (0, -1), (1, 1), (1, -1),
            (-1, 1), (-1, -1)]
        for dx, dy in moves:
            col, row = self.col + dx, self.row + dy
            if 0 <= col < 8 and 0 <= row < 8:
                if (other_piece :=self.board_state[row][col]) is None or other_piece.color != self.color:
                    valid_moves.add((col, row))
        
        valid_moves |= self.castles_valid()
        
        return valid_moves
    def __repr__(self):
        return "K"

class Pawn(FirstMoveMixin, ChessPiece):
    sprite_path = "images/{color}/pawn.png"
    def __init__(self, color, board_state, parent=None):
        super().__init__(color, board_state, parent)
    
    def promote(self):
        print('LOL NIC zatim')
    
    def update_pos(self, **kwargs):
        super().update_pos(**kwargs)
        if self.row == 0 or self.row == 7:
            self.promote()
    
    def get_valid_moves(self):
        valid_moves = set()
        direction = 1 if self.color == "black" else -1
        if self.board_state[self.row + direction][self.col] is None:
            valid_moves.add((self.col, self.row + direction))
        
        if 0 <= self.row + direction < 8 and 0 <= self.col - 1 < 8 \
            and (other_piece:=self.board_state[self.row + direction][self.col - 1]) is not None \
            and other_piece.color != self.color:
            valid_moves.add((self.col - 1, self.row + direction))
        if 0 <= self.row + direction < 8 and 0 <= self.col + 1 < 8 \
            and (other_piece:=self.board_state[self.row + direction][self.col + 1]) is not None  \
            and other_piece.color != self.color:
            valid_moves.add((self.col + 1, self.row + direction)) 
        
        if self.first_move and self.board_state[self.row + 2 * direction][self.col] is None:
            valid_moves.add((self.col, self.row + 2 * direction))
        
        return valid_moves
    def __repr__(self):
        return "P"


class TestPiece(ChessPiece):
    sprite_path = "images/{color}/test.png"
    
    def __init__(self, color, board_state, parent=None):
        super().__init__(color, board_state, parent)
        print(self.pixmap(), self.pixmap().size())

    def get_valid_moves(self):
        # Placeholder implementation for valid moves
        return {(i, j) for i in range(8) for j in range(8)}

    def __repr__(self):
        return "T"

    def __str__(self):
        return "T"