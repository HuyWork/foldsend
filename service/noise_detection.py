import time
import numpy as np
import sounddevice as sd
from PyQt5.QtCore import QRunnable, QThread


class NoiseDetection(QThread):
    def __init__(self):
        super().__init__()
        self.THRESHOLD = 0.001
        self.SAMPLE_RATE = 44100
        self.CHUNK_DURATION = 0.5
        self.DETECTION_TIME = 5

        self.noise_start_time = None
        self.continuous_noise_duration = 0

    def run(self):
        while True:
            audio_data = sd.rec(int(self.SAMPLE_RATE * self.CHUNK_DURATION),
                                samplerate=self.SAMPLE_RATE, channels=1, dtype='float64')
            sd.wait()

            if self.check_noise(audio_data):
                if self.noise_start_time is None:
                    self.noise_start_time = time.time()
                    print('Noise detection started')
                else:
                    self.continuous_noise_duration = time.time() - self.noise_start_time
                    print(self.continuous_noise_duration)

                if self.continuous_noise_duration >= self.DETECTION_TIME:
                    print("noise detected")
                    # thay một sound phát cảnh báo ở đây
            else:
                self.noise_start_time = None
                self.continuous_noise_duration = 0

    def check_noise(self, audio_data):
        amplitude = np.linalg.norm(audio_data) / len(audio_data)
        return amplitude > self.THRESHOLD



