import cv2
import torch
import os
import numpy as np
import pandas as pd
import time 
import csv
from datetime import datetime, timedelta
from ultralytics import YOLO
from deepface import DeepFace
from plyer import notification  # for popups


import sys
print("Python interpreter path:", sys.executable)

def get_student_name(student_id):
    df = pd.read_csv("data/students.csv")
    df["ID num"] = df["ID num"].astype(str).str.strip()
    student_id = str(student_id).strip()
    match = df[df["ID num"] == student_id]
    if not match.empty:
        return match.iloc[0]["full name"]
    return "Unknown"

recent_attendance = {}  # student_id: last_attendance_time

# -----------------------------
# CONFIGURATION
# -----------------------------
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
camera.set(cv2.CAP_PROP_FPS, 30)
with open("camera_started.txt", "w") as f:
    f.write("Camera has started")


model = YOLO(r"C:\Users\Luqman Nurhakim\Desktop\Python\Fyp Zatul\smart attandance\best.pt")
database_path = r"C:\Users\Luqman Nurhakim\Desktop\Python\Fyp Zatul\smart attandance\training_dataset"
attendance_file = "attendance_session2.csv"
if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["ID Number", "Student Name", "Date", "Time"])
    df.to_csv(attendance_file, index=False)

recognized_faces = {}
frame_counter = 0
process_every_n_frame = 10  
last_recognized_name = None
last_recognition_time = 0
display_duration = 3  # seconds

# -----------------------------
# LOAD SUBJECT CODE
# -----------------------------
subject_code = "UNKNOWN"
try:
    with open("current_subject.txt", "r") as f:
        subject_code = f.read().strip()
except Exception as e:
    print("[WARNING] Could not read subject code:", e)


# -----------------------------
# LOG ATTENDANCE
# -----------------------------
def log_attendance(student_id):
    full_name = get_student_name(student_id) or "Unknown"
    now = datetime.now()
    date_str = datetime.now().strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")

    file_path = "attendance_session2.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["ID num", "full name", "Date", "Time", "Subject"])
        writer.writerow([student_id, full_name, date_str, time_str, subject_code])

    print(f"[✅] Logged attendance for {student_id} ({full_name}) at {date_str} {time_str}")

# -----------------------------
# MARK ATTENDANCE
# -----------------------------
def mark_attendance(student_id):
    print(f"[DEBUG] Trying to mark attendance for: {student_id}")
    full_name = get_student_name(student_id)

    if not full_name:
        print(f"[❌] ID {student_id} not found in workers file.")
        notification.notify(title="Attendance Failed", message="Worker ID not found.", timeout=3)
        return

    # ✅ STEP 1: Get the group from students.csv
    group = "UNKNOWN"
    if os.path.exists("data/students.csv"):
        with open("data/students.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["ID num"] == student_id:
                    group = row.get("Group", "UNKNOWN")
                    break

    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")

    file_path = "attendance_session2.csv"

    # Memory check (in this session)
    if student_id in recent_attendance:
        last_time = recent_attendance[student_id]
        if now - last_time < timedelta(hours=1):
            print(f"[MEMORY SKIP] {student_id} already marked in this session.")
            notification.notify(title="Already Marked", message=f"{full_name}'s attendance already recorded.", timeout=3)
            return

    # CSV check (persistent)
    if not os.path.exists(file_path):
        pd.DataFrame(columns=["ID num", "full name", "Group", "Date", "Time", "Subject"]).to_csv(file_path, index=False)

    df = pd.read_csv(file_path)
    if not df.empty and "Date" in df.columns and "Time" in df.columns:
        df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors="coerce")
        student_logs = df[df["ID num"] == student_id]

        if not student_logs.empty:
            last_time = student_logs["datetime"].max()
            if pd.notnull(last_time) and (now - last_time < timedelta(hours=1)):
                print(f"[CSV SKIP] {student_id} already scanned at {last_time.strftime('%H:%M:%S')}")
                notification.notify(title="Already Marked", message=f"{full_name}'s attendance already recorded.", timeout=3)
                return

    # ✅ STEP 2: Get subject code from saved file
    subject_code = "UNKNOWN"
    if os.path.exists("current_subject.txt"):
        with open("current_subject.txt", "r") as f:
            subject_code = f.read().strip()

    # ✅ STEP 3: Write attendance
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([student_id, full_name, group, date_str, time_str, subject_code])

    recent_attendance[student_id] = now
    print(f"[✅] Logged attendance for {student_id} ({full_name})")
    notification.notify(title="Attendance Marked", message=f"{full_name}'s attendance recorded successfully.", timeout=3)

# -----------------------------
# FACE DETECTION
# -----------------------------
def detect_faces(frame):
    results = model(frame)
    faces = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0].item()
            if confidence > 0.6:
                faces.append((x1, y1, x2, y2))
    return faces

# -----------------------------
# FACE RECOGNITION
# -----------------------------
def recognize_face(face_path):
    try:
        embedding = DeepFace.represent(
            img_path=face_path,
            model_name="ArcFace",
            enforce_detection=False,
            detector_backend="opencv"   # add this
        )

        matches = DeepFace.find(
            img_path=face_path,
            db_path=database_path,
            model_name="ArcFace",
            distance_metric="cosine",
            enforce_detection=False,
            detector_backend="opencv"   # add this
        )

        if matches and len(matches[0]) > 0:
            student_name = os.path.basename(matches[0]["identity"][0]).split(".")[0]
            print(f"[INFO] Recognized: {student_name}")
            return student_name
    except Exception as e:
        print("Face recognition error:", e)
    return None

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    frame = cv2.flip(frame, 1)
    faces = detect_faces(frame)
    frame_counter += 1
    current_time = time.time()

    for x1, y1, x2, y2 in faces:
        x1, y1, x2, y2 = max(0, x1 - 10), max(0, y1 - 10), x2 + 10, y2 + 10
        face_crop = frame[y1:y2, x1:x2].copy()
        face_path = "detected_face.jpg"
        cv2.imwrite(face_path, face_crop)

        if frame_counter % process_every_n_frame == 0:
            recognized_name = recognize_face(face_path)
            if recognized_name:
                last_recognized_name = recognized_name
                last_recognition_time = current_time

                # Extract ID from name like "Ajwad_1234"
                if "_" in recognized_name:
                    extracted_id = recognized_name.split("_")[-1]
                else:
                    extracted_id = recognized_name  # fallback if no underscore

                mark_attendance(extracted_id)


        if last_recognized_name and current_time - last_recognition_time < display_duration:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, last_recognized_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, "Unknown", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Smart Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
