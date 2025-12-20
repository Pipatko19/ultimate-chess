from PySide6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

class TimeDisplay(qtw.QWidget):
    
    timer_ended = qtc.Signal()
    
    def __init__(self, parent=None, start_time=480):
        super().__init__(parent)
        
        self.ended = False
        
        layout = qtw.QHBoxLayout(self)
        self.time = start_time
        self.lbl_time = qtw.QLabel(self.str_time, self)
        self.lbl_time.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_time)
    
    @property
    def str_time(self) -> str:
        minutes, seconds = divmod(self.time, 60)
        return f"Time: {minutes:02}:{seconds:02}"
    
    @qtc.Slot()
    def update_time(self):
        if self.ended:
            return
        if self.time <= 0:
            self.ended = True
            self.timer_ended.emit()
        self.time -= 1
        self.lbl_time.setText(self.str_time)