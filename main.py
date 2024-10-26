# region Import Library
import sys
import cv2
import dlib
from PyQt5.QtCore import Qt, QThreadPool, QTime
from PyQt5.QtGui import QImage, QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from service.camera import Camera
from service.chatgpt import ChatGPT
from service.countdown import Countdown
from service.datetime import DateTime
from service.noise_detection import NoiseDetection
from service.notification import Notification
from service.signal import Signal
from ui.main_window import Ui_MainWindow
# endregion

def border_radius(image, radius):
    size = image.size()

    border_img = QImage(size, QImage.Format_ARGB32)
    border_img.fill(Qt.transparent)

    painter = QPainter(border_img)
    painter.setRenderHint(QPainter.Antialiasing)

    path = QPainterPath()
    path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    painter.setClipPath(path)

    painter.drawImage(0, 0, image)
    painter.end()

    return border_img

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.detector = dlib.get_frontal_face_detector()
        self.key = ("sk-proj-kEd4rS5T3se1gaM48OPRl-zUasZkQBcWl9yUQm64TVP9bh_SimLn4Z43Mi6wTThYLdWzp0--MtT3BlbkFJvQ"
                    "z1Gq_3yzvOVodDjjUz_Y-Jb9cD4YhZTpyGcm1pJcCZ7jNlT0xgFGZAmrx1fDH3ajYlPBEogA")
        self.thread_pool = QThreadPool()
        self.signal = Signal()

        self.signal.frame_signal.connect(self.update_frame)
        self.signal.response_signal.connect(self.update_chatgpt_response)

        self.cap = cv2.VideoCapture(0)
        self.timer_id = self.startTimer(30)
        self.check_reset = True

        self.lineEdit.returnPressed.connect(self.send_chatgpt_request)

        self.signal.datetime_signal.connect(self.update_datetime)
        self.signal.face_signal.connect(self.update_faces_detected)

        self.startBtn.clicked.connect(self.start_countdown)
        self.pauseBtn.clicked.connect(self.pause_countdown)
        self.resetBtn.clicked.connect(self.reset_countdown)
        self.setEmailBtn.clicked.connect(self.set_mail)

        self.camera = Camera(self.cap, self.detector, self.signal)
        self.camera.start()

        self.noise_detection = NoiseDetection()
        self.noise_detection.start()

        self.counter = None

    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        border_img = border_radius(q_img, 5)
        self.cameraLbl.setPixmap(QPixmap.fromImage(border_img))

    def update_faces_detected(self, num):
        self.infoLbl.setText(f"Faces detected: {num}")

    def update_chatgpt_response(self, response):
        self.chatgptLbl.setText(response)
        print(response)

    def update_datetime(self, current_time):
        self.dateEdit.setDate(current_time.date())
        self.timeEdit.setTime(current_time.time())

    def update_countdown(self, time):
        self.countDownLbl.setText(time.toString("hh:mm:ss"))

    def send_chatgpt_request(self):
        question = self.lineEdit.text()
        chatgpt = ChatGPT(self.key, question, self.signal)
        self.thread_pool.start(chatgpt)

    def start_countdown(self):
        start_time = self.countdownEdit.time()
        if start_time > QTime(0, 0, 0):
            if self.counter is None or not self.counter.running:
                self.counter = Countdown(start_time, self.signal, parent=self)
                self.signal.countdown_signal.connect(self.update_countdown)
                self.counter.start()
                self.camera.reset_infringe_count()
                self.startBtn.setEnabled(False)
                self.pauseBtn.setEnabled(True)
                self.camera.update_work(True)

    def pause_countdown(self):
        if self.counter:
            if self.pauseBtn.isChecked():
                self.counter.pause()
                self.camera.update_work(False)
            else:
                self.counter.resume()
                self.camera.update_work(True)

    def reset_button(self):
        self.startBtn.setEnabled(True)
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.setChecked(False)

    def end_countdown(self):
        if self.counter:
            self.reset_button()
            self.counter.stop()
            self.counter = None
            self.camera.update_work(False)
            self.camera.send_infringe(True)
        self.signal.infringe_signal.connect(self.send_email)

    def reset_countdown(self):
        if self.counter:
            self.reset_button()
            self.counter.reset()
            self.counter = None
            self.countDownLbl.setText("00:00:00")
            self.camera.update_work(False)

    def set_mail(self):
        mail = self.emailEdit.text()
        if mail.strip():
            self.label.setText(f"{mail}")

    def send_email(self, infringe_count):
        notification = Notification()
        notification.set_information(infringe_count, self.label.text())
        self.thread_pool.start(notification)
        self.signal.infringe_signal.disconnect(self.send_email)


    def timerEvent(self, event):
        # current date time
        current = DateTime(self.signal)
        self.thread_pool.start(current)

    def closeEvent(self, event):
        self.killTimer(self.timer_id)
        self.cap.release()
        self.thread_pool.waitForDone()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = Main()
    window.show()
    sys.exit(app.exec_())

