import time

from PyQt5.QtCore import QThread, QTime, pyqtSignal, QTimer, QRunnable, QMutex, QWaitCondition, QThreadPool


class Countdown(QRunnable):
    def __init__(self, start_time, signal):
        super().__init__()
        self._is_paused = False
        self._is_reset = False
        self.mutex = QMutex()
        self.pause_condition =QWaitCondition()
        self.time_left = start_time
        self.signal = signal

    def run(self):
        while self.time_left > QTime(0, 0, 0):
            self.mutex.lock()
            if self._is_reset:
                self.time_left = QTime(0, 0, 0)
                self._is_reset = False
            if self._is_paused:
                self.pause_condition.wait(self.mutex)
            self.mutex.unlock()

            self.time_left = self.time_left.addSecs(-1)
            self.signal.countdown_signal.emit(self.time_left.toString("hh:mm:ss"))
            QThreadPool.globalInstance().waitForDone(1000)

    def pause(self):
        self.mutex.lock()
        self._is_paused = True
        self.mutex.unlock()

    def reset(self):
        self.mutex.lock()
        self._is_reset = True
        self.pause_condition.wakeAll()
        self.mutex.unlock()
