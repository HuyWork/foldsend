from PyQt5.QtCore import QObject, pyqtSignal, QDateTime


class Signal(QObject):
    frame_signal = pyqtSignal(object)
    face_signal = pyqtSignal(int)
    pose_signal = pyqtSignal(object)
    response_signal = pyqtSignal(str)
    countdown_signal = pyqtSignal(str)
    datetime_signal = pyqtSignal(QDateTime)