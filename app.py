import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import pickle
import numpy as np
import time
import threading
import pyttsx3
import mediapipe as mp
import os
import sys   # ✅ ADDED

# =========================
# SAFE PATH FIX (ADDED ONLY)
# =========================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =========================
# VOICE ENGINE
# =========================
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run, daemon=True).start()


# =========================
# LOAD DATASET (ONLY FIX HERE)
# =========================
def load_dataset():
    with open(resource_path("face_data.pkl"), "rb") as f:   # ✅ ONLY CHANGE
        return pickle.load(f)


# =========================
# EAR FUNCTION
# =========================
def eye_aspect_ratio(face, eye_points, w, h):
    pts = []
    for i in eye_points:
        lm = face.landmark[i]
        pts.append((int(lm.x * w), int(lm.y * h)))

    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))

    return (A + B) / (2.0 * C)


# =========================
# LOGIN
# =========================
def login():
    if entry_user.get() == "admin" and entry_pass.get() == "1234":
        messagebox.showinfo("SUCCESS", "Login Successful")
        speak("Login successful")
        start_camera()
    else:
        messagebox.showerror("ERROR", "Invalid credentials")
        speak("Login failed")


# =========================
# CAMERA SYSTEM
# =========================
def start_camera():

    data = load_dataset()
    known_encodings = data["encodings"]

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        messagebox.showerror("ERROR", "Camera not opening")
        return

    blink_count = 0
    eye_closed = False
    blink_locked = False

    face_verified = False
    unknown_flag = False

    stage = "ENCRYPTED"
    stage_time = time.time()

    access_granted = False
    accuracy = 0

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    LEFT = [33, 160, 158, 133, 153, 144]
    RIGHT = [362, 385, 387, 263, 373, 380]

    while True:

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        result = face_mesh.process(rgb)

        status = "LOOKING FOR FACE"
        crypto_status = ""
        color = (255, 255, 255)

        # =========================
        # FACE RECOGNITION
        # =========================
        if len(encodings) > 0:

            enc = encodings[0]

            matches = face_recognition.compare_faces(known_encodings, enc)
            distances = face_recognition.face_distance(known_encodings, enc)

            if len(distances) > 0:

                best = np.argmin(distances)
                accuracy = int((1 - distances[best]) * 100)
                accuracy = max(0, min(100, accuracy))

                if distances[best] > 0.45 or not matches[best]:

                    unknown_flag = True
                    face_verified = False
                    status = "UNKNOWN PERSON - BLOCKED"
                    color = (0, 0, 255)

                else:

                    unknown_flag = False
                    face_verified = True
                    status = "FACE VERIFIED"
                    color = (0, 255, 0)

            for (top, right, bottom, left) in faces:
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        else:
            unknown_flag = True
            face_verified = False
            status = "NO FACE DETECTED"

        # =========================
        # BLOCK UNKNOWN
        # =========================
        if unknown_flag:
            blink_count = 0
            blink_locked = False
            stage = "ENCRYPTED"
            crypto_status = "ACCESS DENIED"

        # =========================
        # BLINK SYSTEM
        # =========================
        if result.multi_face_landmarks and face_verified and not blink_locked:

            face = result.multi_face_landmarks[0]

            ear = (eye_aspect_ratio(face, LEFT, w, h) +
                   eye_aspect_ratio(face, RIGHT, w, h)) / 2

            if ear < 0.23:
                eye_closed = True
            else:
                if eye_closed:
                    blink_count += 1
                    eye_closed = False

            if blink_count >= 3:
                blink_count = 3
                blink_locked = True
                stage = "DECRYPTED"
                stage_time = time.time()

        # =========================
        # FLOW
        # =========================
        if unknown_flag:
            crypto_status = "SYSTEM LOCKED"

        elif stage == "ENCRYPTED":
            crypto_status = "DATA ENCRYPTED - BLINK 3 TIMES"

        elif stage == "DECRYPTED":
            crypto_status = "DATA DECRYPTED"

            if time.time() - stage_time > 5:
                stage = "ACCESS"

        elif stage == "ACCESS":

            crypto_status = "ACCESS GRANTED"

            if not access_granted:
                access_granted = True
                speak("Access granted")

                cv2.putText(frame,
                            "ACCESS GRANTED",
                            (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            3)

                cv2.imshow("SYSTEM", frame)
                cv2.waitKey(2000)

                cap.release()
                cv2.destroyAllWindows()
                return

        # =========================
        # UI
        # =========================
        cv2.putText(frame, status, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    color, 2)

        cv2.putText(frame,
                    f"Blinks: {blink_count}/3",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2)

        cv2.putText(frame,
                    f"Accuracy: {accuracy}%",
                    (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2)

        cv2.putText(frame,
                    crypto_status,
                    (30, 180),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2)

        cv2.imshow("SECURE AI SYSTEM", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# =========================
# GUI
# =========================
root = tk.Tk()
root.title("Secure AI Authentication System")
root.geometry("420x320")
root.configure(bg="#1e1e2f")

tk.Label(root,
         text="LOGIN SYSTEM",
         font=("Arial", 18, "bold"),
         bg="#1e1e2f",
         fg="white").pack(pady=20)

tk.Label(root,
         text="Username",
         bg="#1e1e2f",
         fg="white").pack()

entry_user = tk.Entry(root)
entry_user.pack(pady=5)

tk.Label(root,
         text="Password",
         bg="#1e1e2f",
         fg="white").pack()

entry_pass = tk.Entry(root, show="*")
entry_pass.pack(pady=5)

tk.Button(root,
          text="LOGIN & START CAMERA",
          command=login,
          bg="#00c896",
          fg="white",
          font=("Arial", 12, "bold")).pack(pady=20)

root.mainloop()