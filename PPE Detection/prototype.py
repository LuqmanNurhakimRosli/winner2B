import tkinter as tk
from tkinter import Label, Button, filedialog
from PIL import Image, ImageTk
from ultralytics import YOLO
import torch
import cv2
import threading
import time
import requests
import os

class PPEApp:
    def __init__(self, window):
        self.window = window
        self.window.title("PPE Detection System")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 700)
        self.window.configure(bg="#222831")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Using device: {self.device}")

        self.model_path = r"C:\\Users\\Luqman Nurhakim\\Downloads\\best.pt"
        if not os.path.isfile(self.model_path):
            print("[ERROR] Set self.model_path to your YOLOv8 weights file (best.pt)")
            raise SystemExit(1)
        self.model = YOLO(self.model_path).to(self.device)

        # Telegram bot setup (optional)
        self.bot_token = "8165098639:AAGvhfSKsEbg86dhL0YK3yPkVKSCb9PeXvs"
        self.chat_id = 763389477
        self.required_classes = {"face-mask", "gloves", "helmet", "shoes", "safety-vest"}
        self.last_missing_time = None
        self.delay_seconds = 10  # Delay between alerts in seconds

        # Main layout: sidebar (left), main panel (right)
        self.sidebar = tk.Frame(window, bg="#393E46", width=220)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = Label(self.sidebar, text="🦺 PPE DETECTION", font=("Arial", 18, "bold"), fg="#FFD369", bg="#393E46", pady=30)
        self.logo_label.pack(fill="x")

        self.upload_btn = Button(self.sidebar, text="Upload Image", font=("Arial", 12), bg="#FFD369", fg="#222831", relief="flat", command=self.upload_image, height=2)
        self.upload_btn.pack(fill="x", padx=20, pady=(10, 5))
        self.start_btn = Button(self.sidebar, text="Start Detection", font=("Arial", 12), bg="#00ADB5", fg="white", relief="flat", command=self.start_camera, height=2)
        self.start_btn.pack(fill="x", padx=20, pady=5)
        self.stop_btn = Button(self.sidebar, text="Stop Detection", font=("Arial", 12), bg="#393E46", fg="#FFD369", relief="flat", command=self.stop_camera, height=2)
        self.stop_btn.pack(fill="x", padx=20, pady=5)

        self.settings_btn = Button(self.sidebar, text="⚙ Settings", font=("Arial", 12), bg="#393E46", fg="#EEEEEE", relief="flat", command=self.open_settings, height=2)
        self.settings_btn.pack(fill="x", padx=20, pady=(30, 10))

        # Main panel
        self.main_panel = tk.Frame(window, bg="#222831")
        self.main_panel.pack(side="left", fill="both", expand=True)

        # Status panel
        self.status_panel = tk.Frame(self.main_panel, bg="#393E46", height=90)
        self.status_panel.pack(fill="x", pady=(0, 10))

        self.alert_label = Label(self.status_panel, text="Detection Status: Not Started", font=("Arial", 16, "bold"), fg="#FFD369", bg="#393E46")
        self.alert_label.pack(side="left", padx=30, pady=20)

        self.missing_label = Label(self.status_panel, text="", font=("Arial", 14), fg="#FF6363", bg="#393E46")
        self.missing_label.pack(side="left", padx=30, pady=20)

        # Canvas for image/video
        self.canvas = tk.Canvas(self.main_panel, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=30, pady=10)
        self.image_container = self.canvas.create_image(0, 0, anchor="nw")

        # Camera / run state
        self.cap = None
        self.running = False
        # Target FPS (can be adjusted)
        self.target_fps = 60
        self.frame_interval = 1.0 / float(self.target_fps)

        self.window.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Dynamically resize canvas and image
        if hasattr(self, 'canvas') and hasattr(self, 'image_container'):
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.canvas.config(width=w, height=h)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
        self.alert_label.config(text="Processing Image...", fg="#00ADB5")
        threading.Thread(target=self.process_image, args=(file_path,), daemon=True).start()

    def process_image(self, file_path):
        img = cv2.imread(file_path)
        results = self.model.predict(img, imgsz=640, conf=0.3, device=self.device)
        annotated = results[0].plot()
        self.window.after(0, lambda: self.display_image(annotated))
        self.window.after(0, lambda: self.alert_label.config(text="Image Detection Complete", fg="#00FFB4"))

    def start_camera(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        # try to request camera FPS (some cameras/drivers ignore this)
        try:
            self.cap.set(cv2.CAP_PROP_FPS, float(self.target_fps))
        except Exception:
            pass
        self.running = True
        self.alert_label.config(text="Starting Camera...", fg="#FFD369")
        threading.Thread(target=self.update_camera_feed, daemon=True).start()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.alert_label.config(text="Detection Stopped", fg="#FF6363")
        self.missing_label.config(text="", fg="#FF6363")

    def update_camera_feed(self):
        prev_time = time.time()
        while self.running and self.cap.isOpened():
            loop_start = time.time()
            ret, frame = self.cap.read()
            if not ret:
                break

            results = self.model.predict(frame, imgsz=640, conf=0.3, device=self.device)
            names = self.model.names
            detected_classes = set([names[int(cls)] for cls in results[0].boxes.cls])

            missing = self.required_classes - detected_classes
            current_time = time.time()

            if missing:
                if self.last_missing_time is None:
                    self.last_missing_time = current_time
                elif current_time - self.last_missing_time >= self.delay_seconds:
                    self.send_telegram_alert(frame, missing)
                    self.last_missing_time = current_time  # Reset timer for next alert

                status_text = f"⚠️ Missing: {', '.join(missing)}"
                status_color = "#FF6363"
            else:
                self.last_missing_time = None
                status_text = "✅ All Required PPE Present"
                status_color = "#00FFB4"

            self.window.after(0, lambda: self.missing_label.config(text=status_text, fg=status_color))

            annotated = results[0].plot()

            # measured fps (processing fps)
            now = time.time()
            measured_fps = 1.0 / max(1e-6, (now - prev_time))
            prev_time = now

            # Throttle to target fps: sleep the remainder of the frame interval
            loop_end = time.time()
            elapsed = loop_end - loop_start
            sleep_time = max(0.0, self.frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

            # Display frame and the measured fps (clamped)
            display_fps = min(measured_fps, self.target_fps)
            self.window.after(0, lambda ann=annotated, f=display_fps: self.display_camera_frame(ann, f))

        if self.cap:
            self.cap.release()

    def display_camera_frame(self, frame, fps):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        frame_rgb = cv2.resize(frame_rgb, (w, h))
        image = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=image)
        self.canvas.itemconfig(self.image_container, image=imgtk)
        self.canvas.image = imgtk
        self.alert_label.config(text=f"Detection Started | FPS: {fps:.2f}", fg="#00FFB4")

    def display_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        frame_rgb = cv2.resize(frame_rgb, (w, h))
        image = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=image)
        self.canvas.itemconfig(self.image_container, image=imgtk)
        self.canvas.image = imgtk

    def open_settings(self):
        # Simple settings dialog (placeholder)
        top = tk.Toplevel(self.window)
        top.title("Settings")
        top.geometry("400x300")
        top.configure(bg="#393E46")
        Label(top, text="Settings", font=("Arial", 16, "bold"), bg="#393E46", fg="#FFD369").pack(pady=20)
        Label(top, text="(Settings UI can be implemented here)", bg="#393E46", fg="#EEEEEE").pack(pady=10)

    def send_telegram_alert(self, image, missing_items):
        if not self.bot_token or not self.chat_id:
            return
        msg = f"🚨 PPE Missing Alert!\nMissing: {', '.join(missing_items)}"
        filename = "ppe_alert.jpg"
        cv2.imwrite(filename, image)
        with open(filename, 'rb') as photo:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            files = {'photo': photo}
            data = {'chat_id': self.chat_id, 'caption': msg}
            response = requests.post(url, files=files, data=data)
            print(f"[INFO] Telegram alert sent. Response: {response.status_code}")

    def on_close(self):
        self.stop_camera()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PPEApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.mainloop()
