# region Import Library
import sys
import cv2
import dlib
from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication
from mediapipe.python.solutions.holistic_test import PoseTest

from thread.camera import Camera
from thread.chatgpt import ChatGPT
from thread.countdown import Countdown
from thread.datetime import DateTime
from thread.pose import Pose
from thread.signal import Signal
from ui.main_window import Ui_MainWindow
# endregion

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.checked_angle = False
        self.setupUi(self)

        self.frame_counter = 0

        self.detector = dlib.get_frontal_face_detector()
        self.key = ("sk-proj-nyhD5Hio676YUn8Sl3xJMU3urjROw3nNKkcLjVpNmy6882LM4CQSy0c73YpR49wnQCo6"
               "ODgVkuT3BlbkFJVsKvVe4dhyAKWjgNnFFQWUyuA7VcEgZCY_6VdSj9JHiuqLzl-f8HCQANxxu9X6"
               "W7bf9mdWxgYA")
        self.thread_pool = QThreadPool()  # Khởi tạo Thread Pool
        self.signal = Signal()

        self.signal.frame_signal.connect(self.update_frame)
        self.signal.face_signal.connect(self.update_faces_detected)
        self.signal.response_signal.connect(self.update_chatgpt_response)
        self.signal.pose_signal.connect(self.check_angle)

        self.cap = cv2.VideoCapture(0)
        self.timer_id = self.startTimer(30)

        self.lineEdit.returnPressed.connect(self.send_chatgpt_request)

        self.signal.datetime_signal.connect(self.update_datetime)

        self.startBtn.clicked.connect(self.start_countdown)
        self.resetBtn.clicked.connect(self.reset_countdown)

        self.countdown = None

        self.pose_timer = QTimer(self)
        self.pose_timer.timeout.connect(self.update_pose)
        self.pose_timer.start(1500)

    def update_pose(self):
        ret, frame = self.cap.read()
        if ret:
            pose = Pose(frame, self.detector, self.signal)
            self.thread_pool.start(pose)

    def update_frame(self, pixmap):
        self.cameraLbl.setPixmap(pixmap)

    def update_faces_detected(self, num):
        self.infoLbl.setText(f"Faces detected: {num}")

    def update_chatgpt_response(self, response):
        self.chatgptLbl.setText(response)
        print(response)

    def update_datetime(self, current_time):
        self.dateEdit.setDate(current_time.date())
        self.timeEdit.setTime(current_time.time())

    def update_countdown(self, countdown):
        self.countDownLbl.setText(countdown)

    def send_chatgpt_request(self):
        question = self.lineEdit.text()
        chatgpt = ChatGPT(self.key, question, self.signal)
        self.thread_pool.start(chatgpt)

    def timerEvent(self, event):
        self.frame_counter += 1
        # current date time
        current = DateTime(self.signal)
        self.thread_pool.start(current)
        # camera
        ret, frame = self.cap.read()
        if ret:
            camera = Camera(frame, self.detector, self.signal, self.checked_angle)
            self.thread_pool.start(camera)

    def check_angle(self, checked):
        self.checked_angle = checked
        print(self.checked_angle)


    def closeEvent(self, event):
        self.killTimer(self.timer_id)
        self.cap.release()
        self.thread_pool.waitForDone()

    def start_countdown(self):
        time = self.countdownEdit.time()

        self.countdown = Countdown(time, self.signal)

        self.signal.countdown_signal.connect(self.update_countdown)

        self.thread_pool.start(self.countdown)

    def reset_countdown(self):
        self.countdown.reset()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = Main()
    window.show()
    sys.exit(app.exec_())

