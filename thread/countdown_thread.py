from PyQt5.QtCore import QThread, QTime, pyqtSignal, QTimer


class Countdown(QThread):
    countdown_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.time_left = QTime(0, 0, 0)

    def run(self):
        while self.running:
            if self.paused:
                self.sleep(1)
                continue

            if self.time_left == QTime(0, 0, 0):
                self.countdown_signal.emit("00:00:00")
                self.running = False
            else:
                self.time_left = self.time_left.addSecs(-1)
                self.countdown_signal.emit(self.time_left.toString("hh:mm:ss"))
            self.sleep(1)

    def start_countdown(self, time_edit):
        self.time_left = time_edit
        self.running = True
        self.paused = False
        if not self.isRunning():
            self.start()

    def pause_countdown(self):
        self.paused = True

    def reset_countdown(self):
        self.paused = True
        self.time_left = QTime(0, 0, 0)
        self.countdown_signal.emit("00:00:00")
        self.running = False

    def stop(self):
        self.running = False
        self.quit()
        self.wait()