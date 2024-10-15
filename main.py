# region Import Library
import sys
from glob import escape

from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from thread.camera_thread import Camera
from thread.chatgpt_thread import ChatGPT
from thread.countdown_thread import Countdown
from thread.datetime_thread import DateTime
from ui.main_window import Ui_MainWindow
# endregion

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.camera_thread = Camera()
        self.camera_thread.frame_signal.connect(self.update_frame)
        self.camera_thread.start()

        self.chatgpt_thread = ChatGPT(api_key="sk-proj-nyhD5Hio676YUn8Sl3xJMU3urjROw3nNKk"
                                                    "cLjVpNmy6882LM4CQSy0c73YpR49wnQCo6ODgVkuT3"
                                                    "BlbkFJVsKvVe4dhyAKWjgNnFFQWUyuA7VcEgZCY_6V"
                                                    "dSj9JHiuqLzl-f8HCQANxxu9X6W7bf9mdWxgYA")
        self.lineEdit.returnPressed.connect(self.ask_chatgpt)
        self.chatgpt_thread.response_signal.connect(self.update_chatgpt_response)
        self.chatgpt_thread.start()

        self.datetime_thread = DateTime()
        self.datetime_thread.datetime_signal.connect(self.update_datetime)
        self.datetime_thread.start()

        self.countdown_thread = Countdown()
        self.countdown_thread.countdown_signal.connect(self.update_countdown)
        self.countdown_thread.start()

        self.startBtn.clicked.connect(self.start_countdown)
        self.pauseBtn.clicked.connect(self.pause_countdown)
        self.resetBtn.clicked.connect(self.reset_countdown)

    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.cameraLbl.setPixmap(pixmap)

    def update_chatgpt_response(self, response):
        self.chatgptLbl.setText(response)
        print(response)

    def update_datetime(self, current_time):
        self.dateEdit.setDate(current_time.date())
        self.timeEdit.setTime(current_time.time())

    def update_countdown(self, countdown):
        self.countDownLbl.setText(countdown)

    def closeEvent(self, event):
        self.camera_thread.stop()
        self.chatgpt_thread.stop()
        self.datetime_thread.stop()
        event.accept()

    def start_countdown(self):
        time = self.countdownEdit.time()
        self.countdown_thread.start_countdown(time)

    def pause_countdown(self):
        self.countdown_thread.pause_countdown()

    def reset_countdown(self):
        self.countdown_thread.reset_countdown()

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

