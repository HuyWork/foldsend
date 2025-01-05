import time
import numpy as np
import pygame
import sounddevice as sd
from PyQt5.QtCore import QRunnable, QThread


class NoiseDetection(QThread):
    def __init__(self):
        super().__init__()
        self.THRESHOLD = 0.001
        self.SAMPLE_RATE = 44100
        self.CHUNK_DURATION = 0.2
        self.DETECTION_TIME = 2

        self.noise_start_time = None
        self.continuous_noise_duration = 0

        pygame.mixer.init()
        self.sound_noise_detected = pygame.mixer.Sound("assets/audio/noise.mp3")

    def run(self):
        while True:
            audio_data = sd.rec(int(self.SAMPLE_RATE * self.CHUNK_DURATION),
                                samplerate=self.SAMPLE_RATE, channels=2 , dtype='float64')
            sd.wait()
            if self.check_noise(audio_data):
                if self.noise_start_time is None:
                    self.noise_start_time = time.time()
                else:
                    self.continuous_noise_duration = time.time() - self.noise_start_time

                if self.continuous_noise_duration >= self.DETECTION_TIME:
                    if not pygame.mixer.get_busy():
                        self.sound_noise_detected.play()
            else:
                self.noise_start_time = None
                self.continuous_noise_duration = 0

    def check_noise(self, audio_data):
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms > self.THRESHOLD



