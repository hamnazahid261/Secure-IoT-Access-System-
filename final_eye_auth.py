import cv2
import numpy as np
import mediapipe as mp
import dataset

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)


def start_auth():

    cap = cv2.VideoCapture(0)

    blink_count = 0
    eye_closed = False

    state = "FACE_DETECT"   # ✔ IMPORTANT STATE MACHINE

    data = dataset.load_dataset()
    stored_template = np.array(data["template"])

    face_verified = False
    stable_frames = 0

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        status = ""

        # =========================
        # STEP 1: FACE DETECT STATE
        # =========================
        if state == "FACE_DETECT":

            status = "FACE DETECTING..."

            if result.multi_face_landmarks:

                face = result.multi_face_landmarks[0]

                face_vector = []
                size = min(len(stored_template)//2, 100)

                for i in range(size):
                    lm = face.landmark[i]
                    face_vector.append(lm.x)
                    face_vector.append(lm.y)

                face_vector = np.array(face_vector)

                min_len = min(len(stored_template), len(face_vector))

                distance = np.linalg.norm(
                    stored_template[:min_len] - face_vector[:min_len]
                ) / (min_len + 1e-6)

                if distance < 1.5:
                    stable_frames += 1
                else:
                    stable_frames = 0

                if stable_frames > 15:
                    state = "FACE_VERIFIED"

        # =========================
        # STEP 2: FACE VERIFIED STATE
        # =========================
        elif state == "FACE_VERIFIED":

            status = "FACE AUTHORIZED ✔"

            if result.multi_face_landmarks:

                face = result.multi_face_landmarks[0]

                LEFT_EYE = [33, 160, 158, 133, 153, 144]
                RIGHT_EYE = [362, 385, 387, 263, 373, 380]

                def ear(face, eye_points):
                    pts = []
                    for i in eye_points:
                        lm = face.landmark[i]
                        pts.append((int(lm.x * w), int(lm.y * h)))

                    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
                    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
                    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
                    return (A + B) / (2.0 * C)

                ear_val = (ear(face, LEFT_EYE) + ear(face, RIGHT_EYE)) / 2

                if ear_val < 0.23:
                    eye_closed = True
                else:
                    if eye_closed:
                        blink_count += 1
                        eye_closed = False

                # =========================
                # FINAL STATE
                # =========================
                if blink_count >= 3:
                    state = "GRANTED"

        # =========================
        # STEP 3: GRANTED STATE
        # =========================
        elif state == "GRANTED":

            status = "ACCESS GRANTED ✔"
            cv2.putText(frame, status, (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            cv2.imshow("AUTH SYSTEM", frame)
            cv2.waitKey(2000)

            cap.release()
            cv2.destroyAllWindows()
            return True

        # =========================
        # UI
        # =========================
        cv2.putText(frame, status, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        if state == "FACE_VERIFIED":
            cv2.putText(frame, f"Blinks: {blink_count}", (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("AUTH SYSTEM", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False