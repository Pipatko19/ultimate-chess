from piece_model import ChessPiece, Knight, Bishop, Rook, Queen, Pawn
from king import King
from board import Board
from typing import TypedDict

class Move(TypedDict):
    type: str
    from_col: int
    from_row: int
    to_col: int
    to_row: int
    
def find_move(valid_moves, to_col, to_row):
    """Helper function to find the move object in valid moves."""
    for move in valid_moves:
        if move["to_col"] == to_col and move["to_row"] == to_row:
            return move
    return None

class MoveGenerator:
    def __init__(self, board_state: Board):
        self.board_state = board_state
        
    def castles_valid(self, king_col: int, king_row: int) -> set[tuple[int, int]]:
        king = self.board_state.get_piece(king_col, king_row)
        valid_castles = set()
        if not king.first_move: #type: ignore
            return valid_castles
        
        # King-side castle (short)
        kingside_rook = self.board_state.get_piece(king_col + 3, king_row)
        if isinstance(kingside_rook, Rook) and kingside_rook.first_move:
            if self.board_state.get_piece(king_col + 1, king_row) is None \
                and self.board_state.get_piece(king_col + 2, king_row) is None:
                valid_castles.add((king_col + 2, king_row))
        
        # Queen-side castle (long)
        queenside_rook = self.board_state.get_piece(king_col - 4, king_row) if king_col - 4 >= 0 else None
        if isinstance(queenside_rook, Rook) and queenside_rook.first_move:
            if self.board_state.get_piece(king_col - 1, king_row) is None \
                and self.board_state.get_piece(king_col - 2, king_row) is None \
                and self.board_state.get_piece(king_col - 3, king_row) is None:
                valid_castles.add((king_col - 2, king_row))
        return valid_castles
        
        
    def find_pins(self, king_col: int, king_row: int, color: str) -> dict[tuple[int, int], frozenset[tuple[int, int]]]:
        """Finds all pieces that are pinning the king."""
        pins = {}
        sliding_directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # horizontal and vertical
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # diagonal  
        ]
        
        for dx, dy in sliding_directions:
            pinned_position = None
            blocking_squares = set()
            col, row = king_col + dx, king_row + dy
            while self.board_state.is_on_board(col, row):
                piece = self.board_state.get_piece(col, row)
                blocking_squares.add((col, row))
                if not piece:
                    col += dx
                    row += dy
                    continue
                if piece.color == color:
                    if pinned_position is None:
                        pinned_position = (col, row)
                    else:
                        break
                else:
                    if isinstance(piece, (Queen, Rook)) and (dx == 0 or dy == 0) or \
                        isinstance(piece, (Queen, Bishop)) and (dx != 0 and dy != 0):
                        if pinned_position:
                            pins[pinned_position] = blocking_squares
                    break
                col += dx
                row += dy
        return pins
    
    def _knight_check(self, king_col: int, king_row: int, color: str) -> tuple[int, set[tuple[int, int]]]:
        """if the king is in check by a knight."""
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        check_count = 0
        blocking_squares = set()
        
        for dx, dy in knight_moves:
            col, row = king_col + dx, king_row + dy
            if self.board_state.is_on_board(col, row):
                piece = self.board_state.get_piece(col, row)
                if isinstance(piece, Knight) and piece.color != color:
                    check_count += 1
                    blocking_squares.add((col, row))
        return (check_count, blocking_squares)
    

    def _sliding_check(self, king_col: int, king_row: int, color: str) -> tuple[int, set[tuple[int, int]]]:
        sliding_directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # horizontal and vertical
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # diagonal
        ]
        
        check_count = 0
        blocking_squares = set()
        
        for dx, dy in sliding_directions:
            col, row = king_col + dx, king_row + dy
            potential_blocking = {(col, row)}
            
            while self.board_state.is_on_board(col, row):
                piece = self.board_state.get_piece(col, row)
                if piece is None:
                    col += dx
                    row += dy
                    potential_blocking.add((col, row))
                    continue
                if piece.color == color:
                    break
                if isinstance(piece, (Queen, Rook)) and (dx == 0 or dy == 0) or \
                    isinstance(piece, (Queen, Bishop)) and (dx != 0 and dy != 0):
                    blocking_squares |= potential_blocking
                    check_count += 1
                    break
                break
        
        return (check_count, blocking_squares)

    def _pawn_check(self, king_col: int, king_row: int, color: str) -> tuple[int, set[tuple[int, int]]]:
        """if the king is in check by a pawn."""
        if color == "white":
            pawn_moves = [(-1, -1), (1, -1)]
        else:
            pawn_moves = [(-1, 1), (1, 1)]
        
        check_count = 0
        blocking_squares = set()
        
        for dx, dy in pawn_moves:
            col, row = king_col + dx, king_row + dy
            if self.board_state.is_on_board(col, row):
                piece = self.board_state.get_piece(col, row)
                if isinstance(piece, Pawn) and piece.color != color:
                    check_count += 1
                    blocking_squares.add((col, row))
        return (check_count, blocking_squares)
        
    def in_check(self, color: str, king_col=None, king_row=None) -> tuple[int, set[tuple[int, int]]]:
        """Returns the number of checks on the king."""
        if king_col is None or king_row is None:
            king_col, king_row = self.board_state.find_king_position(color)
            
        checks = (f(king_col, king_row, color) for f in [
            self._sliding_check,
            self._knight_check,
            self._pawn_check
        ])
        
        check_count, blocking_squares = zip(*checks)
        total_checks = sum(check_count)
        total_blocking_squares = set().union(*blocking_squares)

        return total_checks, total_blocking_squares
    
    def _filter_moves(self, piece: ChessPiece, col: int, row: int) -> set[tuple[int, int]]:
        valid_moves = piece.get_valid_moves(self.board_state, col, row)
        
        king_col, king_row = self.board_state.find_king_position(piece.color)
        check_count, blocking_squares = self.in_check(piece.color, king_col, king_row)
        
        if not isinstance(piece, King):
            match check_count:
                case 0:    
                    pins = self.find_pins(king_col, king_row, piece.color)
                    if (col, row) in pins:
                        blockable = pins[(col, row)]
                        valid_moves = valid_moves & blockable
                case 1:
                    valid_moves = {move for move in valid_moves if move in blocking_squares}
                case _:
                    valid_moves = set()
        else:
            valid_moves = self._handle_king(piece.color, valid_moves)
            valid_moves |= self.castles_valid(king_col, king_row)
            print("VALID MOVES", valid_moves)
        return valid_moves
    
    def _format_moves(self, valid_moves: set[tuple[int, int]], piece: ChessPiece, col: int, row: int) -> list[Move]:
        formatted_moves: list[Move] = []
        
        for to_col, to_row in valid_moves:
            move = Move(type="normal", from_col=col, from_row=row, to_col=0, to_row=0)
            if isinstance(piece, King) and abs(to_col - col) == 2:
                move['type'] = "castle"
            elif (captured_piece := self.board_state.get_piece(to_col, to_row)) is not None:
                if captured_piece.color == piece.color:
                    continue
                move['type'] = "capture"
                

            move['to_col'] = to_col
            move['to_row'] = to_row
            formatted_moves.append(move)
        return formatted_moves
        
    def _handle_king(self, color: str, moves: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Check if the king is in check after a move."""
        new_moves = set()
        for col, row in moves:
            if self.in_check(color, col, row)[0] == 0:
                new_moves.add((col, row))
        return new_moves
    
    def generate_moves(self, piece: ChessPiece, col: int, row: int) -> list[Move]:
        filtered_moves = self._filter_moves(piece, col, row)
        formatted_moves = self._format_moves(filtered_moves, piece, col, row)
        
        return formatted_moves


