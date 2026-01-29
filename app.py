import streamlit as st
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

st.set_page_config(page_title="Dental Infection Control System", layout="centered")

# ---------------- DATABASE INITIALIZATION ----------------
def init_db():
    # Streamlit Cloud writable folder
    DB_PATH = "/tmp/database.db"
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Responses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        knowledge INTEGER NOT NULL,
        awareness INTEGER NOT NULL,
        practice INTEGER NOT NULL
    )
    """)

    # Insert default admin if not exists
    cur.execute("SELECT 1 FROM users WHERE email=?", ("admin@test.com",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (email, password, role) VALUES (?,?,?)",
            ("admin@test.com", generate_password_hash("admin123"), "admin")
        )

    conn.commit()
    conn.close()
    return DB_PATH

# Initialize DB and get path
DB_PATH = init_db()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🦷 Dental Infection Control System")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            st.session_state.logged_in = True
            st.session_state.role = user[3]
            st.success("Login successful!")
            st.stop()  # stop current run so dashboard will show on next run
        else:
            st.error("Invalid credentials")

# ---------------- STUDENT DASHBOARD ----------------
elif st.session_state.role == "student":
    st.subheader("🧑‍🎓 Student Dashboard")
    st.info("Please answer all questions honestly. Your responses are confidential.")

    # Questionnaire
    st.markdown("### SECTION A: Knowledge")
    k1 = st.radio("Autoclaving is used to:", ["Destroy microorganisms", "Clean instruments"])
    k2 = st.radio("Which is a sterilization method?", ["Steam sterilization", "Washing with water"])
    knowledge = (1 if k1 == "Destroy microorganisms" else 0) + \
                (1 if k2 == "Steam sterilization" else 0)

    st.markdown("### SECTION B: Awareness")
    a1 = st.slider("Wearing gloves reduces infection risk", 1, 3)
    a2 = st.slider("Hand hygiene is essential", 1, 3)
    awareness = a1 + a2

    st.markdown("### SECTION C: Practice")
    p1 = st.slider("I sterilize instruments after each use", 1, 3)
    p2 = st.slider("I wear PPE during procedures", 1, 3)
    practice = p1 + p2

    if st.button("Submit Assessment"):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO responses (knowledge, awareness, practice) VALUES (?,?,?)",
            (knowledge, awareness, practice)
        )
        conn.commit()
        conn.close()

        st.success("Assessment submitted successfully!")

        st.markdown("### 📊 Your Results")
        st.write("Knowledge Score:", knowledge)
        st.write("Awareness Score:", awareness)
        st.write("Practice Score:", practice)
        st.info("Recommendation: Improve adherence to infection control guidelines.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.stop()  # stop current run to return to login page

# ---------------- ADMIN DASHBOARD ----------------
elif st.session_state.role == "admin":
    st.subheader("🧑‍💼 Admin Dashboard")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()

    st.write("### Collected Responses")
    st.dataframe(df)

    if not df.empty:
        st.write("### 📈 Average Scores")
        averages = df[["knowledge", "awareness", "practice"]].mean()
        st.bar_chart(averages)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.stop()  # stop current run to return to login page
