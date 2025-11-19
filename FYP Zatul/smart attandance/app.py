import streamlit as st

st.set_page_config(page_title="Smart Attendance System", layout="centered")


import base64
import os

# Step 1: Convert image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Step 2: Apply image as background
def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call function with uploaded file using absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "pages", "AI.png")
set_background(bg_path)

# Your existing CSS and layout here
st.markdown("""
<style>
/* Keep your UI styling */
.title-container {
    background-color: rgba(255,255,255,0.9);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 30px;
    text-align: center;
}
.title-container h1 {
    font-size: 38px;
    font-weight: 800;
    color: #003366;
    margin-bottom: 10px;
}
.title-container h3 {
    font-size: 18px;
    color: #666666;
}
.stButton > button {
    width: 270px;
    height: 50px;
    background-color: #3EC6FF;
    color: black;
    font-size: 18px;
    font-weight: 600;
    border: none;
    border-radius: 12px;
    margin: 12px 0px;
    transition: transform 0.2s ease;
    box-shadow: 0 0 12px #3EC6FF, 0 0 20px #3EC6FF;
}
.stButton > button:hover {
    background-color: #00bfff;
    box-shadow: 0 0 18px #3EC6FF, 0 0 35px #3EC6FF;
    transform: scale(1.03);
}
.button-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 30px;
}
.footer {
    margin-top: 50px;
    font-size: 14px;
    color: #666666;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<div style='margin-top: 320px;'>", unsafe_allow_html=True)

# Mobile-friendly instructions
st.markdown("""
<div style='background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
    <h4 style='color: #003366; margin-bottom: 15px;'>📱 Mobile-Friendly Features</h4>
    <p style='color: #666666; font-size: 14px; margin: 5px 0;'>✅ Use your phone's camera for attendance</p>
    <p style='color: #666666; font-size: 14px; margin: 5px 0;'>✅ Upload photos from your gallery</p>
    <p style='color: #666666; font-size: 14px; margin: 5px 0;'>✅ Works on any device with internet</p>
</div>
""", unsafe_allow_html=True)

# Buttons (centered)
# Centered buttons using Streamlit columns
col1, col2, col3 = st.columns([1, 2, 1])  # col2 will hold the buttons centered

with col2:
    if st.button("📷 Start Face Recognition", help="Use your mobile camera for attendance"):
        st.switch_page("pages/FaceRecognition.py")
    if st.button("🔐 Login"):
        st.switch_page("pages/Login.py")
    if st.button("📝 Sign Up"):
        st.switch_page("pages/SignUp.py")
    if st.button("❌ Exit"):
        st.warning("You can now close the tab.")

st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <div class="footer">
         © 2025 Smart Attendance System based Face Recognition by Nurizzatul Faryisha Binti Rosli
    </div>
""", unsafe_allow_html=True)