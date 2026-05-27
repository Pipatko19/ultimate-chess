from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg
from chess.MoveTypes import Move, MoveType

class HistoryDisplay(qtw.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(222, 300)
        
        self.view = qtw.QTableView(parent=self)
        self.view.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.model = qtg.QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels(["#", "White", "Black"])
        self.view.setModel(self.model)
        
        header = self.view.horizontalHeader()

        header.setSectionResizeMode(0, qtw.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, qtw.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, qtw.QHeaderView.ResizeMode.Stretch)
        
        fm = self.view.fontMetrics()
        width = fm.horizontalAdvance("mmm")
        header.resizeSection(0, width)

        self.view.setEditTriggers(qtw.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setSelectionMode(qtw.QAbstractItemView.SelectionMode.NoSelection)
        self.view.setFocusPolicy(qtc.Qt.FocusPolicy.NoFocus)
        self.view.setShowGrid(False)
        self.view.verticalHeader().setVisible(False)
        self.view.setAlternatingRowColors(True)

        self.view.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)
        
        layout = qtw.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
    
    def _format_move(self, move: Move) -> str:
        piece = str(move['piece'])
        to_col = move['to_col']
        to_row = move['to_row']
        notation = ""
        if MoveType.CASTLE & move['type']:
            if to_col == 6:
                notation = "O-O"
            else:
                notation = "O-O-O"
        else:
            if piece.upper() != 'P':
                notation += piece.upper()
            if MoveType.CAPTURE & move['type']:
                if piece.lower() == 'p':
                    notation += chr(move['from_col'] + ord('a'))
                notation += "x"
            notation += chr(to_col + ord('a')) + str(8 - to_row)

            if MoveType.PROMOTION & move['type']:
                notation += "=" + str(move['promotion_piece']).upper()
        if MoveType.CHECKMATE & move['type']:
            notation += "#"
        elif MoveType.STALEMATE & move['type']:
            notation += "½-½"
        elif MoveType.CHECK & move['type']:
            notation += "+"

        if MoveType.EN_PASSANT & move['type']:
            notation += " e.p."

        return notation
    
    def add_move(self, move: Move, color: str) -> None:
        print("Adding move to history:", move, color)
        formatted_move = self._format_move(move)
        if color == "white":
            self._white_move(formatted_move)
        else:
            self._black_move(formatted_move)
    
    def _white_move(self, move: str) -> None:
        row = self.model.rowCount()
        self.model.appendRow([])
        self.model.setItem(row, 0, qtg.QStandardItem(str(row + 1)))
        self.model.setItem(row, 1, qtg.QStandardItem(move))
    def _black_move(self, move: str) -> None:
        row = self.model.rowCount() - 1
        self.model.setItem(row, 2, qtg.QStandardItem(move))
    
if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    history_display = HistoryDisplay()
    history_display.resize(200, 300)
    history_display.show()
    sys.exit(app.exec())