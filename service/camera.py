import time

import cv2
import dlib
import numpy as np
import mediapipe as mp
import pygame
from PyQt5.QtCore import QThread, pyqtSlot


def get_eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

class Camera(QThread):
    def __init__(self, cap, detector, signal):
        super().__init__()
        self.cap = cap
        self.detector = detector
        self.signal = signal
        self.running = True
        self.COUNTER = 0
        self.sleeping_detected_start_time = None
        self.last_sound_play_time = 0
        self.cooldown_time = 10
        self.LOOKING_AWAY_COUNTER = 0
        self.last_alert_time = time.time() - self.cooldown_time
        self.working = False
        self.check_infringe = False
        self.change_pose = True

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=0, min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)

        self.predictor = dlib.shape_predictor("service/shape_predictor_68_face_landmarks.dat")
        self.EYE_AR_THRESHOLD = 0.2
        self.LOOKING_AWAY_THRESHOLD = 0.3

        pygame.mixer.init()
        self.sound_hand_detected = pygame.mixer.Sound("assets/audio/tinhtao.mp3")
        self.sound_sleeping = pygame.mixer.Sound("assets/audio/bdng.mp3")
        self.sound_looking_away = pygame.mixer.Sound("assets/audio/mttt.mp3")

        self.infringe_count = None

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            if self.working:
                self.process_pose(frame)
                self.process_hand(frame, faces)
                self.process_face(frame, faces, gray)
            else:
                cv2.putText(frame, 'Relax Time', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                            cv2.LINE_AA)
                if self.check_infringe:
                    self.check_infringe = False
                    self.signal.infringe_signal.emit(self.infringe_count)
            self.process_face_detection(frame, faces)
            self.signal.frame_signal.emit(frame)
            self.signal.face_signal.emit(len(faces))


    def process_face_detection(self, frame, faces):
        for face in faces:
            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    def process_face(self, frame, faces, gray):
        for face in faces:
            landmarks = self.predictor(gray, face)
            for i in range(0, 68):
                x, y = landmarks.part(i).x, landmarks.part(i).y
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

            ear_left = get_eye_aspect_ratio(left_eye)
            ear_right = get_eye_aspect_ratio(right_eye)
            ear = (ear_left + ear_right) / 2.0

            if ear < self.EYE_AR_THRESHOLD:
                self.COUNTER += 1
                if self.COUNTER >= 1:
                    current_time = time.time()
                    if ear < self.EYE_AR_THRESHOLD:
                        if self.sleeping_detected_start_time is None:
                            self.sleeping_detected_start_time = time.time()
                        else:
                            elapsed_time_since_sleeping_detected = time.time() - self.sleeping_detected_start_time
                            if elapsed_time_since_sleeping_detected >= 1 and (
                                    time.time() - self.last_sound_play_time) >= 1:
                                if not pygame.mixer.get_busy():
                                    self.infringe_count["sleeping"] += 1
                                    self.sound_sleeping.play()
                                    self.last_sound_play_time = time.time()
                                    self.sleeping_detected_start_time = None

            else:
                self.sleeping_detected_start_time = None

            if ear > self.LOOKING_AWAY_THRESHOLD:
                self.LOOKING_AWAY_COUNTER += 1
                if self.LOOKING_AWAY_COUNTER >= 1:
                    current_time = time.time()
                    if current_time - self.last_alert_time > self.cooldown_time:
                        self.infringe_count["looking_away"] += 1
                        if not pygame.mixer.get_busy():
                            self.sound_looking_away.play()
                            self.last_alert_time = current_time

            else:
                self.LOOKING_AWAY_COUNTER = 0

    def process_pose(self, frame):
        pose_result = self.pose.process(frame)
        try:
            landmarks = pose_result.pose_landmarks.landmark
            nose = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.NOSE.value].y]
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            angle = calculate_angle(nose, shoulder, hip)
            if 120 <= angle <= 240:
                cv2.putText(frame, 'Back straight', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                            cv2.LINE_AA)
                self.change_pose = False
            else:
                cv2.putText(frame, 'Arched back', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                            cv2.LINE_AA)
                if not self.change_pose:
                    self.infringe_count["posture"] += 1
                    self.change_pose = True
        except Exception as e:
            print(e)

    def process_hand(self, frame, faces):
        hand_results = self.hands.process(frame)

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for face in faces:
                    face_bbox = dlib.rectangle(face.left(), face.top(), face.right(), face.bottom())
                    for lm in hand_landmarks.landmark:
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        if face_bbox.left() < cx < face_bbox.right() and face_bbox.top() < cy < face_bbox.bottom():
                            if not pygame.mixer.get_busy():
                                self.infringe_count["hand_detected"] += 1
                                self.sound_hand_detected.play()

    @pyqtSlot(object)
    def update_work(self, working):
        self.working = working

    @pyqtSlot(object)
    def send_infringe(self, checked):
        self.check_infringe = checked

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def reset_infringe_count(self):
        self.infringe_count = {"posture": 0, "hand_detected": 0, "sleeping": 0, "looking_away": 0}