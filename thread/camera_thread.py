import cv2
from PyQt5.QtCore import QThread, pyqtSignal

class Camera(QThread):
    frame_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_signal.emit(rgb_frame)
        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()