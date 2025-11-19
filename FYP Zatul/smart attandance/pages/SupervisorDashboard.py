import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import urllib.request

# Set page config
st.set_page_config(page_title="Supervisor Dashboard", layout="wide")

# === Define helper function first ===
def build_attendance_summary(subject, group, date_str):
    present_ids = []
    if os.path.exists("attendance_session2.csv"):
        df = pd.read_csv("attendance_session2.csv")
        df["Date"] = df["Date"].astype(str)
        for _, row in df.iterrows():
            try:
                if (
                    datetime.strptime(row['Date'].strip(), "%d/%m/%Y").date() == datetime.strptime(date_str.strip(), "%d/%m/%Y").date() and
                    row['Subject'].strip().lower() == subject.strip().lower() and
                    row['Group'].strip().upper() == group.strip().upper()
                ):
                    present_ids.append(str(row['ID num']).strip())
            except:
                continue

    students = []
    if os.path.exists("data/students.csv"):
        df_students = pd.read_csv("data/students.csv")
        df_students["ID num"] = df_students["ID num"].astype(str).str.strip()
        students = df_students[df_students["Group"].str.upper() == group.upper()]

    summary = []
    for _, student in students.iterrows():
        summary.append({
            "Name": student["full name"],
            "ID": student["ID num"],
            "Group": student["Group"],
            "Status": "Present" if student["ID num"] in present_ids else "Absent"
        })
    return pd.DataFrame(summary)

# Initialize session state for view
if 'view' not in st.session_state:
    st.session_state['view'] = None

# CSS styling
st.markdown("""
<style>
/* === Global Background and Font === */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
    color: white;
}
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: white;
}

/* === Main Title and Subtext === */
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

/* === Glowing Buttons === */
.stButton > button, button[data-testid="baseButton-element"] {
    width: 320px;
    height: 52px;
    background: linear-gradient(90deg, #3EC6FF, #00bfff) !important;
    color: #001a26 !important;
    font-size: 16px;
    font-weight: 700;
    border: none !important;
    border-radius: 12px !important;
    margin: 10px 0px;
    transition: transform .15s ease, box-shadow .2s ease;
    box-shadow: 0 6px 16px rgba(0,191,255,.35);
}
.stButton > button:hover, button[data-testid="baseButton-element"]:hover {
    background-color: #00bfff !important;
    transform: scale(1.05);
    box-shadow: 0 0 20px #3EC6FF, 0 0 35px #3EC6FF;
}

/* === Download Button Glow === */
div[data-testid="stDownloadButton"] > button {
    width: 320px !important;
    height: 52px !important;
    background: linear-gradient(90deg, #3EC6FF, #00bfff) !important;
    color: #001a26 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    margin: 10px 0px !important;
    box-shadow: 0 6px 16px rgba(0,191,255,.35);
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px) scale(1.01);
    box-shadow: 0 10px 22px rgba(0,191,255,.45);
}

/* === Date input styling === */
div[data-testid="stDateInput"] > div {
    width: 100% !important;
}
div[data-testid="stDateInput"] input {
    height: 48px !important;
    font-size: 16px !important;
    color: white;
    background-color: rgba(255, 255, 255, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Display title and user
full_name = st.session_state.get('full_name', 'SUPERVISOR').upper()
st.markdown("<div class='main-title'>Supervisor Dashboard</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-text'>Logged in as: <b>{full_name}</b></div>", unsafe_allow_html=True)

# === Main Dashboard ===
if st.session_state['view'] is None:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("View Registered Workers", key="btn_view_registered"):
            st.session_state['view'] = 'registered'
        if st.button("Check Attendance", key="btn_check_attendance"):
            st.session_state['view'] = 'attendance'
        if st.button("View My Profile", key="btn_view_profile"):
            st.session_state['view'] = 'profile'
        if st.button("Logout", key="btn_logout"):
            for key in ['full_name', 'ID num', 'email', 'profile', 'role']:
                st.session_state.pop(key, None)
            st.success("Logged out successfully.")
            st.switch_page("app.py")
        st.markdown("<div class='ai-tag'>Powered by AI • Smart Face Recognition System</div>", unsafe_allow_html=True)
# === Registered Workers View ===
elif st.session_state['view'] == 'registered':
    st.subheader("📋 Registered Workers")
    if os.path.exists("data/students.csv"):
        df = pd.read_csv("data/students.csv")
        df_display = df.drop(columns=["password", "profile"], errors="ignore")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.error("workers (students.csv) not found.")

    if st.button(" Back", key="back_from_registered"):
        st.session_state['view'] = None
        st.rerun()

# === Attendance Checking ===
elif st.session_state['view'] == 'attendance':
    st.subheader("📋 Check Attendance by Site")
    st.markdown("<hr>", unsafe_allow_html=True)


    subject = st.text_input("🏗️ Enter Site Code", placeholder= "e.g. SITE-01")
    group = st.text_input("👷 Enter Crew", placeholder= "e.g. Crew A")
    selected_date = st.date_input("📅 Enter Date", value=datetime.now(), format="DD/MM/YYYY")
    date_str = selected_date.strftime("%d/%m/%Y")

    st.markdown("</div>", unsafe_allow_html=True)  # End of styled form

    # Buttons aligned side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(" Show Attendance", key="btn_show_attendance"):
            if not subject.strip():
                st.warning("⚠️ Please enter Site Code.")
            elif not group.strip():
                st.warning("⚠️ Please enter Crew.")
            elif not date_str.strip():
                st.warning("⚠️ Please enter Date.")
            else:
                st.session_state['att_subject'] = subject
                st.session_state['att_group'] = group
                st.session_state['att_date'] = date_str
                st.session_state['view'] = 'attendance_result'
                st.rerun()

    with col2:
        if st.button(" Back", key="back_from_attendance"):
            st.session_state['view'] = None
            st.rerun()

# === Attendance Result View ===
elif st.session_state['view'] == 'attendance_result':
    st.title("📊 Attendance Summary")

    subject = st.session_state.get('att_subject', '')
    group = st.session_state.get('att_group', '')
    date_str = st.session_state.get('att_date', '')

    df_result = build_attendance_summary(subject, group, date_str)

    if not df_result.empty:
        st.dataframe(df_result, use_container_width=True)
        filename = f"attendance_summary_{subject}_{group}_{date_str.replace('/', '-')}.csv"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                "Download CSV",
                df_result.to_csv(index=False).encode('utf-8'),
                file_name=filename,
                use_container_width=True
            )

            if st.button(" Back", key="back_to_form"):
                st.session_state['view'] = 'attendance'
                st.rerun()

# === Profile View ===
elif st.session_state['view'] == 'profile':
    staff_id = str(st.session_state.get("ID num", "")).strip()

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

    if os.path.exists("data/staff.csv"):
        df = pd.read_csv("data/staff.csv")
        df["ID num"] = df["ID num"].astype(str).str.strip()
        staff = df[df["ID num"] == staff_id]
        if not staff.empty:
            name = staff.iloc[0]["full name"]
            email = staff.iloc[0]["email"]
            profile = staff.iloc[0].get("profile", "default_avatar.jpg").replace("\\", "/")
            profile_img = profile if image_exists(profile) else "default_avatar.jpg"

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### 👤 My Profile", unsafe_allow_html=True)

                col_img, col_info = st.columns([1, 2])
                with col_img:
                    profile_image = st.session_state.get('profile', 'default_avatar.jpg')
                    if os.path.exists(profile_image):
                        st.image(profile_image, width=130)
                    else:
                        st.image("default_avatar.jpg", width=130)

                with col_info:
                    st.write(f"**Full Name :** {st.session_state.get('full_name', '')}")
                    st.write(f"**ID Number :** {st.session_state.get('ID num', '')}")
                    email = st.session_state.get('email', '')
                    st.markdown(f"**Email     :** <a href='mailto:{email}'>{email}</a>", unsafe_allow_html=True)
                    st.write(f"**Role      :** {st.session_state.get('role', '')}")

        else:
            st.error("No profile found.")
    else:
        st.error("staff.csv not found.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Back", key="back_from_profile"):
            st.session_state['view'] = None
            st.rerun()
