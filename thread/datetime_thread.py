from PyQt5.QtCore import QThread, pyqtSignal, QDateTime


class DateTime(QThread):
    datetime_signal = pyqtSignal(QDateTime)
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            current_datetime = QDateTime.currentDateTime()
            self.datetime_signal.emit(current_datetime)
            self.sleep(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()