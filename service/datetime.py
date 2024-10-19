from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QRunnable


class DateTime(QRunnable):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def run(self):
            current_datetime = QDateTime.currentDateTime()
            self.signal.datetime_signal.emit(current_datetime)
