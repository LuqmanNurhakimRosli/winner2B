import streamlit as st
import pandas as pd
import os
import requests
from PIL import Image as PILImage
from datetime import datetime
import base64

# --- Page and Style Configuration ---
st.set_page_config(page_title="Worker Sign-Up", layout="centered")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: white;
    }
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    .main-title {
        font-size: 38px;
        font-weight: 800;
        text-align: center;
        color: white;
        margin-bottom: 5px;
    }
    .sub-text {
        text-align: center;
        font-size: 18px;
        color: #dddddd;
        margin-bottom: 40px;
    }
    .stButton > button {
        width: 250px;
        height: 50px;
        background-color: #3EC6FF !important;
        color: black !important;
        font-size: 18px;
        border: none;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 0 12px #3EC6FF, 0 0 20px #3EC6FF;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #00bfff !important;
        transform: scale(1.05);
        box-shadow: 0 0 20px #3EC6FF, 0 0 35px #3EC6FF;
    }
    .upload-box {
        border: 2px dashed #ccc;
        padding: 20px;
        text-align: center;
        background-color: #fafafa;
        border-radius: 10px;
        color: #999;
    }
    .file-uploader {
        margin-top: 8px;
    }
    .password-strength {
        font-size: 14px;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Path Setup ---
students_file = "data/students.csv"
staff_file = "data/staff.csv"
profile_dir = "profile_pics"
training_dir = "training_dataset"
os.makedirs(profile_dir, exist_ok=True)
os.makedirs(training_dir, exist_ok=True)

# --- Roboflow Detection Function ---
def roboflow_detect(image_path):
    api_key = "vNanG7jZa0IZIAx2MVR5"
    endpoint = "https://detect.roboflow.com/passport-images-opm09/2"
    with open(image_path, "rb") as image_file:
        response = requests.post(
            f"{endpoint}?api_key={api_key}&confidence=40&overlap=30",
            files={"file": image_file},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    if response.status_code == 200:
        return response.json().get("predictions", [])
    else:
        st.warning("[WARNING] Roboflow error. Fallback to manual preprocessing.")
        return []

# --- Image Processing Function ---
def process_profile_image(uploaded_file, full_name, id_number):
    profile_filename = f"{full_name.replace(' ', '_')}_{id_number}.jpg"
    profile_path = os.path.join(profile_dir, profile_filename)
    training_path = os.path.join(training_dir, profile_filename)

    with open(profile_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        predictions = roboflow_detect(profile_path)
        if predictions:
            pred = predictions[0]
            x, y, width, height = pred["x"], pred["y"], pred["width"], pred["height"]
            image = PILImage.open(profile_path)
            img_width, img_height = image.size
            left = max(0, x - width / 2) - 20
            top = max(0, y - height / 2) - 20
            right = min(img_width, x + width / 2) + 20
            bottom = min(img_height, y + height / 2) + 20
            cropped = image.crop((left, top, right, bottom)).resize((224, 224))
            cropped.save(training_path)
        else:
            raise Exception("No face detected")
    except:
        image = PILImage.open(profile_path)
        image = image.resize((640, 640))
        image.save(training_path)

    return profile_path

# --- Registration UI ---
st.title("Worker Registration")
st.subheader("Fill in worker/supervisor details")
with st.container():
    with st.form("signup_form"):
        st.markdown('<div class="form-style">', unsafe_allow_html=True)

        full_name = st.text_input("Full Name", placeholder="e.g. Ali Bin Abu")
        id_number = st.text_input("Worker ID", placeholder="e.g. WKR00123")
        role = st.radio("Role", ["Worker", "Supervisor"], horizontal=True)
        group = st.text_input("Crew", placeholder="e.g. Crew A") if role == "Worker" else "-"
        email = st.text_input("Email", placeholder="e.g. worker@site.com")
        password = st.text_input("Password", type="password", placeholder="Enter a strong password")

        # --- Password Strength Indicator ---
        if password:
            strength = "Weak"
            if len(password) > 8 and any(c.isdigit() for c in password) and any(c.isupper() for c in password):
                strength = "Strong"
            elif len(password) > 6:
                strength = "Moderate"
            st.markdown(f"<div class='password-strength'>Password strength: <b>{strength}</b></div>", unsafe_allow_html=True)

        # --- File Upload with Styled Box ---
        image_file = st.file_uploader("Upload worker face image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

        # --- Profile Image Preview ---
        if image_file:
            image = PILImage.open(image_file)
            st.image(image, caption="Preview", width=150)

        submitted = st.form_submit_button("Register")

        st.markdown("</div>", unsafe_allow_html=True)

# --- Form Submission Handling ---
if submitted:
    if not all([full_name, id_number, email, password]):
        st.error("Please fill in all required fields.")
    # Relax ID/email format checks for construction context
    else:
        csv_file = students_file if role == "Worker" else staff_file

        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
        else:
            df = pd.DataFrame(columns=["full name", "ID num", "Group", "email", "password", "profile", "role"])

        if id_number in df["ID num"].astype(str).values:
            st.error("ID Number already registered.")
        elif email in df["email"].astype(str).values:
            st.error("Email already registered.")
        else:
            profile_img_path = "default_avatar.jpg"
            if image_file is not None:
                profile_img_path = process_profile_image(image_file, full_name, id_number)

            new_user = {
                "full name": full_name,
                "ID num": id_number,
                "Group": group,
                "email": email,
                "password": password,
                "profile": profile_img_path,
                "role": role
            }

            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            df.to_csv(csv_file, index=False)

            # Store session and redirect
            st.session_state['full_name'] = full_name
            st.session_state['ID num'] = id_number
            st.session_state['Group'] = group
            st.session_state['email'] = email
            st.session_state['profile'] = profile_img_path
            st.session_state['role'] = role

            st.success("Registration successful! Redirecting to dashboard...")
            st.switch_page("pages/WorkerDashboard.py" if role == "Worker" else "pages/SupervisorDashboard.py")

# --- Back Button ---
if st.button("Back"):
    st.switch_page("app.py")
    
st.markdown("<div class='ai-tag'>Powered by AI • Smart Face Recognition System</div>", unsafe_allow_html=True)