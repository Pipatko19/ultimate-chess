from __future__ import annotations
from typing import TYPE_CHECKING
from piece_model import FirstMoveMixin, ChessPiece


if TYPE_CHECKING:
    from board import Board
    
class King(FirstMoveMixin, ChessPiece):    
        
    # def castles_valid(self) -> set[tuple[int, int]]:
    #     valid_castles = set()
    #     if not self.first_move:
    #         return valid_castles
        
    #     # King-side castle (short)
    #     kingside_rook = self.board_state.get_piece(col + 3, row)
    #     if isinstance(kingside_rook, Rook) and kingside_rook.first_move:
    #         if self.board_state.get_piece(col + 1, row) is None \
    #             and self.board_state.get_piece(col + 2, row) is None:
    #             valid_castles.add((col + 2, row))
        
    #     # Queen-side castle (long)
    #     queenside_rook = self.board_state.get_piece(col - 4, row) if col - 4 >= 0 else None
    #     if isinstance(queenside_rook, Rook) and queenside_rook.first_move:
    #         if self.board_state.get_piece(col - 1, row) is None \
    #             and self.board_state.get_piece(col - 2, row) is None \
    #             and self.board_state.get_piece(col - 3, row) is None:
    #             valid_castles.add((col - 2, row))
    #     return valid_castles
    
    # def castle(self, target_col: int):
    #     row = self.row
    #     col = self.col

    #     # Kingside castle
    #     if target_col == col + 2:
    #         rook_col = col + 3
    #         rook = self.board_state.get_piece(rook_col, row)
    #         self.board_state.place_piece(rook, col + 1, row)
    #         self.board_state.place_piece(None, rook_col, row)

    #     # Queenside castle
    #     elif target_col == col - 2:
    #         rook_col = col - 4
    #         rook = self.board_state.get_piece(rook_col, row)
    #         self.board_state.place_piece(rook, col - 1, row)
    #         self.board_state.place_piece(None, rook_col, row)

    #     else:
    #         return False  # not a castling move

    #     # Move the king
    #     self.board_state.place_piece(self, target_col, row)
    #     self.board_state.place_piece(None, col, row)


    #     rook.update_pos()
    #     self.update_pos()
    #     return True

    
    def get_valid_moves(self, board_state: Board, this_col: int, this_row: int) -> set[tuple[int, int]]:
        valid_moves = set()
        moves = [
            (1, 0), (-1, 0), (0, 1),
            (0, -1), (1, 1), (1, -1),
            (-1, 1), (-1, -1)]
        for dx, dy in moves:
            col, row = this_col + dx, this_row + dy
            if board_state.is_on_board(col, row):
                valid_moves.add((col, row))
        
        #valid_moves |= self.castles_valid()
        
        return valid_moves
    def __repr__(self):
        return "K"