import piece_model

BOARD = [
    "RNBQKBNR",
    "PPPPPPPP",
    "........",
    "........",
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
PIECES = {
    'R': piece_model.Rook,
    'N': piece_model.Knight,
    'B': piece_model.Bishop,
    'Q': piece_model.Queen,
    'K': piece_model.King,
    'P': piece_model.Pawn,
    'T': piece_model.TestPiece
}

def board_parser(board: list[str]) -> list[list[piece_model.ChessPiece | None]]:
    """
    Parses a chess board represented as a list of strings into a 2D list of ChessPiece objects.
    
    Args:
        board (list[str]): A list of strings representing the chess board.
    
    Returns:
        list[list[chess_pieces.ChessPiece]]: A 2D list of ChessPiece objects.
    """

    
    parsed_board = []
    half_point = len(board) // 2
    
    for idx, row in enumerate(board):
        color = "black" if idx <= half_point else "white"
        parsed_row = []
        for piece in row:
            if piece == ".":
                parsed_row.append(None)
            else:
                parsed_row.append(PIECES[piece](color))
        parsed_board.append(parsed_row)
    return parsed_board
    
