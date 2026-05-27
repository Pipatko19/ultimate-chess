from chess.board_model import Board
from chess.move_generator import MoveGenerator, find_move
from chess.piece_model import ChessPiece

from chess.MoveTypes import Move, MoveType, MoveEffect

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
    
    
    def start(self, board) -> Board:
        """Initialize the game state."""
        for row in range(8):
            for col in range(8):
                piece_model = board[row][col]
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
        #we save the moves, so it can be used when the piece is released
        
        return self._valid_moves

    def evaluate_move(self, from_col:int, from_row:int, to_col:int, to_row:int) -> tuple[Move, MoveEffect]|None:
        """Check if the piece and move are valid and return the move."""
        piece = self.board_model.get_piece(from_col, from_row)
        if piece is None or piece.color != self.current_turn:
            return None
        
        move = find_move(self._valid_moves, to_col, to_row)
        if move is None:
            return None
        
        move, move_effect = self._create_move_effect(move)

        return move, move_effect
    
    def _create_move_effect(self, move: Move) -> tuple[Move, MoveEffect]:
        """Create a MoveEffect object based on the given move."""
        from_pos = (move["from_col"], move["from_row"])
        to_pos = (move["to_col"], move["to_row"])
        moved = [(from_pos, to_pos)]
        
        move_effect = MoveEffect(moved_pieces=moved)
        
        
        move_type = move["type"]
        
        if MoveType.CAPTURE & move_type:
            move_effect.captured = (to_pos)
        elif MoveType.EN_PASSANT & move_type:
            move_effect.captured = (move["to_col"], move["from_row"])
        if MoveType.PROMOTION & move_type:
            move_effect.promotion = self.current_turn
        if MoveType.DOUBLE_PAWN_MOVE & move_type:
            move_effect.double_move = (to_pos)

        if MoveType.CASTLE & move_type:
            if move["to_col"] == 6:  # Kingside
                move_effect.moved_pieces.append( ( (7, move["from_row"]), (5, move["from_row"]) ) )
            elif move["to_col"] == 2:  # Queenside
                move_effect.moved_pieces.append( ( (0, move["from_row"]), (3, move["from_row"]) ) )
        
        move, move_effect = self.try_move(move, move_effect)
        
        return move, move_effect

    def update_board(self, move_effect: MoveEffect) -> None:
        """Update the board model based on the move effect."""

        if move_effect.captured:
            self.board_model.remove_piece(*move_effect.captured)
        if move_effect.double_move:
            self.move_generator.set_en_passant(*move_effect.double_move, self.current_turn)
        else:
            self.move_generator.reset_en_passant()
        
        for from_pos, to_pos in move_effect.moved_pieces:
            self.board_model.move_piece(*from_pos, *to_pos)
        
        return None
    
    def on_promotion(self, col:int, row:int, piece: ChessPiece):
        """Handle the promotion of a pawn to a new piece."""
        self.board_model.place_piece(piece, col, row)
    
    def is_selectable(self, col:int, row:int) -> bool:
        """Check if the piece at the given position can be selected."""
        piece = self.board_model.get_piece(col, row)
        return piece is not None and piece.color == self.current_turn
    
    def check_final_state(self, color: str):
        """Check if the given color is in check, checkmate, or stalemate."""
        in_check = self.move_generator.in_check(color)[0] > 0
        legal_moves = [
            move for col, row, piece in self.board_model.yield_all_pieces(color)
            for move in self.move_generator.generate_moves(piece, col, row)
        ]
        print("IN CHECK:", in_check)
        print("LEGAL MOVES:", len(legal_moves))
        if len(legal_moves) < 5:
            print(legal_moves)

        if not legal_moves:
            return MoveType.CHECKMATE if in_check else MoveType.STALEMATE
        elif in_check:
            return MoveType.CHECK
        else:
            return MoveType.NORMAL
    
    def try_move(self, move: Move, effect: MoveEffect) -> tuple[Move, MoveEffect]:
        move = move.copy()
        this_piece = self.board_model.get_piece(move["from_col"], move["from_row"])
        other_piece = self.board_model.get_piece(move["to_col"], move["to_row"])
        self.board_model.move_piece(move["from_col"], move["from_row"], move["to_col"], move["to_row"])
        
        
        other = "black" if self.current_turn == "white" else "white"

        move["type"] |= self.check_final_state(other)

        effect.check = bool(move["type"] & MoveType.CHECK)
        effect.checkmate = bool(move["type"] & MoveType.CHECKMATE)
        effect.stalemate = bool(move["type"] & MoveType.STALEMATE)
        
        self.board_model.place_piece(other_piece, move["to_col"], move["to_row"])
        self.board_model.place_piece(this_piece, move["from_col"], move["from_row"])
        
        return move, effect
        