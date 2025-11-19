import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import urllib.request

st.set_page_config(page_title="Worker Dashboard", layout="centered")

# --- Initialize view state ---
if 'view' not in st.session_state:
    st.session_state['view'] = 'dashboard'

# --- Get worker ID from session ---
student_id = st.session_state.get('ID num', '')
csv_path = "data/students.csv"

# --- Load Worker Info ---
if student_id and os.path.exists(csv_path):
    df_students = pd.read_csv(csv_path)
    df_students["ID num"] = df_students["ID num"].astype(str).str.strip()
    match = df_students[df_students["ID num"] == student_id]

    if not match.empty:
        st.session_state['full_name'] = match.iloc[0]["full name"]
        st.session_state['Group'] = match.iloc[0]["Group"]
        st.session_state['email'] = match.iloc[0]["email"]
        st.session_state['profile'] = match.iloc[0].get("profile", "default_avatar.jpg")
        st.session_state['role'] = match.iloc[0].get("role", "Student")

# --- Welcome Header Styling ---
full_name = st.session_state.get('full_name', 'WORKER').upper()

st.markdown(f"""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0;'>Worker Dashboard</h2>
        <p style='opacity:0.9;margin-top:6px;'>Logged in as: <b>{full_name}</b></p>
    </div>
""", unsafe_allow_html=True)

# --- Button Styling ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
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
        width: 320px;
        height: 52px;
        background: linear-gradient(90deg, #3EC6FF, #00bfff);
        color: #001a26;
        font-size: 16px;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        margin: 10px 0px;
        transition: transform .15s ease, box-shadow .2s ease;
        box-shadow: 0 6px 16px rgba(0,191,255,.35);
    }

    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 10px 22px rgba(0,191,255,.45);
    }

    .card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 18px 18px 8px 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }

    h2 {
        color: white;
        font-weight: 800;
    }
    h5 {
        color: #dddddd;
        font-weight: 500;
    }

    .ai-tag {
        text-align: center;
        color: #dddddd;
        margin-top: 30px;
        font-size: 16px;
        font-style: italic;
    }

    .ai-icon {
        text-align: center;
        font-size: 50px;
        color: white;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# === DASHBOARD MAIN MENU ===
if st.session_state['view'] == 'dashboard':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("View My Attendance"):
            st.session_state['view'] = 'attendance'
        if st.button("View Profile"):
            st.session_state['view'] = 'profile'
        if st.button("Logout"):
            for key in ['full_name', 'ID num', 'Group', 'email', 'profile', 'role', 'view']:
                st.session_state.pop(key, None)
            st.success("You have been logged out.")
            st.switch_page("app.py")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='ai-tag'>Powered by AI • Smart Face Recognition System</div>", unsafe_allow_html=True)
        
# === ATTENDANCE PAGE ===
elif st.session_state['view'] == 'attendance':
    st.title("📅 My Attendance")
    file_path = "attendance_session2.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df["ID num"] = df["ID num"].astype(str).str.strip()
        df["Date"] = df["Date"].astype(str).str.strip()

        # Filter for current worker
        df = df[df["ID num"] == student_id]

        st.markdown("### Select Date")
        col1, col2 = st.columns([5, 1])

        with col1:
            manual_date = st.text_input("Enter date (dd/mm/yyyy)", placeholder="dd/mm/yyyy")

        with col2:
            picked_date = st.date_input(" ", value=None, format="DD/MM/YYYY")

        # Determine which date to use
        selected_date = None
        if manual_date:
            selected_date = manual_date.strip()
        elif picked_date:
            selected_date = picked_date.strftime("%d/%m/%Y")

        # Filter by date if selected
        if selected_date:
            df = df[df["Date"] == selected_date]

        st.write(f"Total Sessions: {len(df)}")
        if not df.empty:
            st.table(df[["Subject", "Date", "Time"]].sort_values(by="Date", ascending=False).reset_index(drop=True))
        else:
            st.warning("No attendance record found.")
    else:
        st.error("Attendance file not found.")

    if st.button(" Back"):
        st.session_state['view'] = 'dashboard'


# === PROFILE PAGE ===
elif st.session_state['view'] == 'profile':
    st.title("👤 My Profile")

    def is_url(path):
        try:
            result = urllib.parse.urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False

    def image_exists(path):
        try:
            if is_url(path):
                with urllib.request.urlopen(path) as response:
                    return response.status == 200
            return os.path.exists(path)
        except:
            return False

    col1, col2 = st.columns([1, 3])
    with col1:
        profile_image = st.session_state.get('profile', 'default_avatar.jpg')
        if image_exists(profile_image):
            st.image(profile_image, width=120)
        else:
            st.image("default_avatar.jpg", width=120)

    with col2:
        st.write(f"**Full Name :** {st.session_state.get('full_name', '')}")
        st.write(f"**ID Number :** {st.session_state.get('ID num', '')}")
        st.write(f"**Group     :** {st.session_state.get('Group', '')}")
        
        email = st.session_state.get('email', '')
        st.markdown(f"**Email     :** <a href='mailto:{email}'>{email}</a>", unsafe_allow_html=True)
        
        st.write(f"**Role      :** {st.session_state.get('role', '')}")

    if st.button(" Back"):
        st.session_state['view'] = 'dashboard'
