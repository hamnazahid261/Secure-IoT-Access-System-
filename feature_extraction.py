import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# eye landmark indexes (MediaPipe)
LEFT_EYE = [33, 133, 160, 159, 158, 144]
RIGHT_EYE = [362, 385, 387, 386, 373, 380]

def get_eye_features(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return None

    landmarks = results.multi_face_landmarks[0].landmark

    def eye_aspect_ratio(eye):
        A = np.linalg.norm(np.array([landmarks[eye[1]].x, landmarks[eye[1]].y]) -
                           np.array([landmarks[eye[5]].x, landmarks[eye[5]].y]))
        B = np.linalg.norm(np.array([landmarks[eye[2]].x, landmarks[eye[2]].y]) -
                           np.array([landmarks[eye[4]].x, landmarks[eye[4]].y]))
        C = np.linalg.norm(np.array([landmarks[eye[0]].x, landmarks[eye[0]].y]) -
                           np.array([landmarks[eye[3]].x, landmarks[eye[3]].y]))
        return (A + B) / (2.0 * C)

    left_ear = eye_aspect_ratio(LEFT_EYE)
    right_ear = eye_aspect_ratio(RIGHT_EYE)

    return [left_ear, right_ear]