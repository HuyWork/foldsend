from PyQt5.QtCore import QObject, pyqtSignal, QDateTime


class Signal(QObject):
    frame_signal = pyqtSignal(object)
    face_signal = pyqtSignal(int)
    response_signal = pyqtSignal(str)
    countdown_signal = pyqtSignal(object)
    infringe_signal = pyqtSignal(object)
    datetime_signal = pyqtSignal(QDateTime)