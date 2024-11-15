import pygame
from PyQt5.QtCore import QTime, QThread


class Countdown(QThread):
    def __init__(self, start_time, signal, parent=None):
        super().__init__(parent)
        self.start_time = start_time
        self.remaining_time = start_time
        self.signal = signal
        self.paused = False
        self.running = True

        pygame.mixer.init()
        self.relax_time = pygame.mixer.Sound("assets/audio/relax.mp3")

    def run(self):
        while self.remaining_time > QTime(0, 0, 0) and self.running:
            if not self.paused:
                self.remaining_time = self.remaining_time.addSecs(-1)
                self.signal.countdown_signal.emit(self.remaining_time)
            self.sleep(1)
        pygame.mixer.stop()
        self.relax_time.play()
        self.parent().end_countdown()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.quit()

    def reset(self):
        self.quit()
        self.terminate()