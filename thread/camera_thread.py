import cv2
from PyQt5.QtCore import QThread, pyqtSignal

class CameraThread(QThread):
    frame_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_signal.emit(frame)
        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()