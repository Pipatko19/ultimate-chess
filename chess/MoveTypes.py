from dataclasses import dataclass
from chess.piece_model import ChessPiece
from typing import TypedDict
from enum import Flag, auto

Pos = tuple[int, int]

class MoveType(Flag):
    NORMAL = auto()
    CAPTURE = auto()
    CASTLE = auto()
    PROMOTION = auto()
    EN_PASSANT = auto() 
    DOUBLE_PAWN_MOVE = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()

class Move(TypedDict):
    """represents an input; what the user could do"""
    type: MoveType
    piece: ChessPiece
    from_col: int
    from_row: int
    to_col: int
    to_row: int
    promotion_piece: ChessPiece | None
    
@dataclass
class MoveEffect:
    """represents a consequence; what the user did"""
    moved_pieces: list[tuple[Pos, Pos]]  # List of (from_position, to_position)
    captured: Pos | None = None
    promotion: str | None = None #color
    double_move: Pos | None = None
    
    check: bool = False
    checkmate: bool = False
    stalemate: bool = False
