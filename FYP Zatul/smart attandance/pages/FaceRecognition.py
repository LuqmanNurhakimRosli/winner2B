import streamlit as st
import time
import subprocess
import os
import sys

st.set_page_config(page_title="Start Attendance", layout="wide")
st.title("📷 Construction Attendance System")

# --- Input Site Code ---
st.subheader("Step 1: Enter Site Code")
subject = st.text_input("Enter site code for this session", placeholder= "e.g. SITE-01")

if st.button("Start Attendance"):
    if not subject:
        st.warning("Please enter a site code.")
    else:
        # Save subject code to file
        with open("current_subject.txt", "w") as f:
            f.write(subject)

        # Remove previous signal if it exists
        signal_file = "camera_started.txt"
        if os.path.exists(signal_file):
            os.remove(signal_file)

        # Start real-time camera script
        try:
            subprocess.Popen([sys.executable, "pages/try_deep.py"])
        except Exception as e:
            st.error(f"Failed to launch camera: {e}")
            st.stop()

        # Spinner while waiting for the camera to start
        with st.spinner("Launching camera, please wait..."):
            for _ in range(200):  # wait up to 100 seconds
                if os.path.exists(signal_file):
                    st.success("✅ Camera is now running. You may proceed to scan your face.")
                    break
                time.sleep(0.5)
            else:
                st.error("❌ Camera did not start in time. Please check your webcam and try again.")

# --- Back Button ---
# Custom styled back button
# --- Custom style for Back button ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: white;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: white;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }

    .stButton > button {
        width: 320px;
        height: 50px;
        background-color: #3EC6FF !important;
        color: black !important;
        font-size: 16px;
        font-weight: 600;
        border: none !important;
        border-radius: 10px !important;
        margin: 12px 0px;
        transition: all 0.3s ease;
        box-shadow: 0 0 12px #3EC6FF, 0 0 20px #3EC6FF;
    }

    .stButton > button:hover {
        background-color: #00bfff !important;
        transform: scale(1.05);
        box-shadow: 0 0 20px #3EC6FF, 0 0 35px #3EC6FF;
    }

    .label {
        font-weight: bold;
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)


# --- Actual working back button ---
if st.button("   Back   "):
    st.switch_page("app.py")

st.markdown("<div class='ai-tag'>Powered by AI • Smart Face Recognition System</div>", unsafe_allow_html=True)