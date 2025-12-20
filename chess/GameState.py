from chess.board_model import Board
from chess.move_generator import MoveGenerator, find_move, MoveType, Move
from board_initializer import BOARD, TEST_BOARD, board_parser
from chess.piece_model import ChessPiece
from dataclasses import dataclass

Pos = tuple[int, int]

@dataclass
class MoveEffect:
    moved: list[tuple[Pos, Pos]]  # List of (from_position, to_position)
    captured: Pos | None = None
    promotion: str | None = None #color
    
    check: bool = False
    checkmate: bool = False
    stalemate: bool = False
    

class GameState:
    def __init__(self):
        self.board_model = Board()
        self.move_generator = MoveGenerator(self.board_model)
        self.current_turn = "white"
        self._valid_moves = list()
        
    def switch_turn(self):
        """Switch the turn between players."""
        self.current_turn = "black" if self.current_turn == "white" else "white"
        print(f"It's now {self.current_turn}'s turn.")
    
    def get_snapshot(self) -> list[list[ChessPiece | None]]:
        """Get the current state of the board."""
        return self.board_model.board
    
    def start(self, board = BOARD) -> Board:
        """Initialize the game state."""
        self.current_turn = "white"
        classed_board = board_parser(board)
        
        for row in range(8):
            for col in range(8):
                piece_model = classed_board[row][col]
                if piece_model is None:
                    continue
                
                #data config
                self.board_model.place_piece(piece_model, col, row)
        
        print(self.board_model)
        return self.board_model
    
    def generate_moves(self, col:int, row:int):
        """Get valid moves for a piece at a given position."""
        piece = self.board_model.get_piece(col, row)
        if piece is None or piece.color != self.current_turn:
            return []
        
        self._valid_moves = self.move_generator.generate_moves(piece, col, row)
        return self._valid_moves

    def evaluate_move(self, from_col:int, from_row:int, to_col:int, to_row:int) -> tuple[Move, MoveEffect]|None:
        """Evaluate and return a move if it's valid."""
        piece = self.board_model.get_piece(from_col, from_row)
        if piece is None or piece.color != self.current_turn:
            return None
        
        move = find_move(self._valid_moves, to_col, to_row)
        if move is None:
            return None
        
        move_effect = self._update_board(move)

        return move, move_effect
    
    def _update_board(self, move: Move) -> MoveEffect:
        """Create a MoveEffect object based on the given move and update the board model"""
        from_pos = (move["from_col"], move["from_row"])
        to_pos = (move["to_col"], move["to_row"])
        moved = [(from_pos, to_pos)]

        
        print(move)
        
        move_type = move["type"]    
        captured = None
        promotion = None
        
        if MoveType.CAPTURE & move_type:
            captured = (to_pos)
            self.board_model.remove_piece(*to_pos)
        if MoveType.PROMOTION & move_type:
            promotion = self.current_turn
        if MoveType.EN_PASSANT & move_type:
            captured = (move["to_col"], move["from_row"])
            self.board_model.remove_piece(move["to_col"], move["from_row"])
        if MoveType.DOUBLE_PAWN_MOVE & move_type:
            self.move_generator.set_en_passant(move["to_col"], move["to_row"], self.current_turn)
        else:
            self.move_generator.reset_en_passant()
        if MoveType.CASTLE & move_type:
            if move["to_col"] == 6:  # Kingside
                moved.append( ( (7, move["from_row"]), (5, move["from_row"]) ) )
                self.board_model.move_piece(7, move["from_row"], 5, move["from_row"])
            elif move["to_col"] == 2:  # Queenside
                moved.append( ( (0, move["from_row"]), (3, move["from_row"]) ) )
                self.board_model.move_piece(0, move["from_row"], 3, move["from_row"])
                
        self.board_model.move_piece(*from_pos, *to_pos)
        

        
        # Check for ending positions
        other = "black" if self.current_turn == "white" else "white"
        
        move["type"] |= self.evaluate_position(other)
        
        check = bool(MoveType.CHECK & move["type"])
        checkmate = bool(MoveType.CHECKMATE & move["type"])
        stalemate = bool(MoveType.STALEMATE & move["type"])
        print(self.board_model)
        
        return MoveEffect(
            moved=moved,
            captured=captured,
            promotion=promotion,
            check=check,
            checkmate=checkmate,
            stalemate=stalemate
        )
    
    def on_promotion(self, piece: ChessPiece, col:int, row:int):
        """Handle the promotion of a pawn to a new piece."""
        self.board_model.place_piece(piece, col, row)
    
    
    def is_selectable(self, col:int, row:int) -> bool:
        """Check if the piece at the given position can be selected."""
        piece = self.board_model.get_piece(col, row)
        return piece is not None and piece.color == self.current_turn
    
    def evaluate_position(self, color: str):
        in_check = self.move_generator.in_check(color)[0] > 0
        legal_moves = [
            move for col, row, piece in self.board_model.yield_all_pieces(color)
            for move in self.move_generator.generate_moves(piece, col, row)
        ]
        
        if not legal_moves:
            return MoveType.CHECKMATE if in_check else MoveType.STALEMATE
        elif in_check:
            return MoveType.CHECK
        else:
            return MoveType.NORMAL