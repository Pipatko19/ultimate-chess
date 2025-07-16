import chess_pieces

BOARD = [
    "RNBQKBNR",
    "PPPPPPPP",
    "........",
    "...T....",
    "........",
    "........",
    "PPPPPPPP",
    "RNBQKBNR"
]

TEST_BOARD = [
    "........",
    "........",
    "......N.",
    "....R...",
    "........",
    "...R.P..",
    "........",
    "........",
]

def board_parser(board: list[str]) -> list[list[chess_pieces.ChessPiece | None]]:
    """
    Parses a chess board represented as a list of strings into a 2D list of ChessPiece objects.
    
    Args:
        board (list[str]): A list of strings representing the chess board.
    
    Returns:
        list[list[chess_pieces.ChessPiece]]: A 2D list of ChessPiece objects.
    """
    pieces = {
        'R': chess_pieces.Rook,
        'N': chess_pieces.Knight,
        'B': chess_pieces.Bishop,
        'Q': chess_pieces.Queen,
        'K': chess_pieces.King,
        'P': chess_pieces.Pawn,
        'T': chess_pieces.TestPiece
    }
    
    parsed_board = []
    half_point = len(board) // 2
    
    for idx, row in enumerate(board):
        color = "black" if idx <= half_point else "white"
        parsed_row = []
        for piece in row:
            if piece == ".":
                parsed_row.append(None)
            else:
                parsed_row.append(pieces[piece](color))
        parsed_board.append(parsed_row)
    return parsed_board
    
