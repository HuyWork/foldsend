import cv2
import dlib
import numpy as np
from PyQt5.QtCore import QRunnable, Qt
from PyQt5.QtGui import QImage, QPainter, QPainterPath
from PyQt5.QtGui import QPixmap

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


def get_eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


class Camera(QRunnable):
    def __init__(self, frame, detector, signal, checked_angel):
        super().__init__()
        self.frame = frame
        self.detector = detector
        self.signal = signal
        self.checked_angel = checked_angel

    def run(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        faces = self.process_face(frame)

        if self.checked_angel:
            cv2.putText(frame, 'Back straight', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                        cv2.LINE_AA)
        else:
            cv2.putText(frame, 'Arched back', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_AA)

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        border_img = border_radius(q_img, 5)
        self.signal.frame_signal.emit(QPixmap.fromImage(border_img))
        self.signal.face_signal.emit(len(faces))

    def process_face(self, frame):
        faces = self.detector(frame, 0)
        for face in faces:
            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return faces

