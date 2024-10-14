# region Import Library
import sys
import cv2
import openai
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication

from thread.camera_thread import CameraThread
from thread.chatgpt_thread import ChatGPTThread
from ui.main_window import Ui_MainWindow
# endregion

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.update_frame)
        self.camera_thread.start()

        self.chatgpt_thread = ChatGPTThread(api_key="sk-proj-nyhD5Hio676YUn8Sl3xJMU3urjROw3nNKk"
                                                    "cLjVpNmy6882LM4CQSy0c73YpR49wnQCo6ODgVkuT3"
                                                    "BlbkFJVsKvVe4dhyAKWjgNnFFQWUyuA7VcEgZCY_6V"
                                                    "dSj9JHiuqLzl-f8HCQANxxu9X6W7bf9mdWxgYA")
        self.lineEdit.returnPressed.connect(self.ask_chatgpt)
        self.chatgpt_thread.response_signal.connect(self.update_chatgpt_response)
        self.chatgpt_thread.start()

    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.cameraLbl.setPixmap(pixmap)

    def update_chatgpt_response(self, response):
        self.chatGPTLbl.setText(response)
        print(response)

    def closeEvent(self, event):
        self.camera_thread.stop()
        self.chatgpt_thread.stop()
        event.accept()

    @staticmethod
    def border_radius(image, radius):
        size = image.size()

        border_img = QImage(size, QImage.Format_ARGB32)
        border_img.fill(Qt.transparent)  # Nền trong suốt

        painter = QPainter(border_img)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
        painter.setClipPath(path)

        painter.drawImage(0, 0, image)
        painter.end()

        return border_img

    def ask_chatgpt(self):
        question = self.lineEdit.text()
        self.chatgpt_thread.ask_chatgpt(question)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = Main()
    window.show()
    sys.exit(app.exec_())

