import streamlit as st
import pandas as pd

st.set_page_config(page_title="Login", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Full background gradient */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: white;
    }

    html, body, [class*="css"] {
        color: white;
        font-family: 'Poppins', sans-serif;
    }

    /* Glassmorphic Card (optional, if you wrap content in .login-card) */
    .login-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 40px;
        max-width: 500px;
        margin: auto;
    }

    /* Title in white */
    .login-title {
        font-size: 40px;
        text-align: center;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }

    /* Input field styling */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: none;
    }

    /* Radio buttons centered */
    .stRadio > div {
        justify-content: center;
    }

    /* Neon buttons */
    .stButton > button {
        width: 250px;
        height: 50px;
        background-color: #3EC6FF; /* soft light blue */
        color: black;
        font-size: 18px;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        box-shadow: 0 0 12px #3EC6FF, 0 0 20px #3EC6FF;
        transition: 0.3s ease-in-out;
    }

    .stButton > button:hover {
        background-color: #00bfff;
        box-shadow: 0 0 18px #3EC6FF, 0 0 35px #3EC6FF;
        transform: scale(1.05);
    }

    /* AI label */
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

st.markdown("<div class='ai-icon'>🤖</div>", unsafe_allow_html=True)

# --- Title ---
st.markdown("<div class='login-title'>Construction Attendance Login</div>", unsafe_allow_html=True)

# --- Centered Login Form ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    role = st.radio("Select your role", ["Worker", "Supervisor"])
    id_number = st.text_input("Worker ID")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn_form"):
        try:
            # Reuse existing CSVs to avoid migration: workers -> students.csv, supervisors -> staff.csv
            file = "data/students.csv" if role == "Worker" else "data/staff.csv"
            df = pd.read_csv(file)

            # Normalize column names to lowercase
            df.columns = [col.strip().lower() for col in df.columns]

            # Clean and strip input + CSV values
            df["id num"] = df["id num"].astype(str).str.strip()
            df["password"] = df["password"].astype(str).str.strip()
            id_number = id_number.strip()
            password = password.strip()

            # Matching logic
            match = df[
                (df["id num"] == id_number) &
                (df["password"] == password)
            ]

            if not match.empty:
                user_data = match.iloc[0]

                # --- Store in Session State ---
                st.session_state['ID num'] = user_data['id num']
                st.session_state['full_name'] = user_data.get('full name', 'Unknown')
                st.session_state['group'] = user_data.get('group', 'N/A')  # Crew might not exist in staff.csv
                st.session_state['email'] = user_data.get('email', '')
                st.session_state['profile'] = user_data.get('profile', 'default_avatar.jpg')
                st.session_state['role'] = role

                st.success("Login successful!")

                if role == "Worker":
                    st.session_state['view'] = 'dashboard'  # Initialize worker view
                    st.switch_page("pages/WorkerDashboard.py")
                else:
                    st.session_state['view'] = None  # Initialize supervisor view
                    st.switch_page("pages/SupervisorDashboard.py")
            else:
                st.error("Invalid ID or password.")

        except FileNotFoundError:
            st.error(f"CSV file not found: {file}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Back button to go to home
    if st.button("Back"):
        st.switch_page("app.py")

    st.markdown("<div class='ai-tag'>Powered by AI • Smart Face Recognition System</div>", unsafe_allow_html=True)
