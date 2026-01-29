import streamlit as st
import sqlite3
import pandas as pd
from werkzeug.security import check_password_hash

st.set_page_config(page_title="Dental Infection Control System", layout="centered")

def get_db():
    return sqlite3.connect("database.db")

# ---------------- LOGIN ----------------
st.title("🦷 Dental Infection Control System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()

        if user and check_password_hash(user[2], password):
            st.session_state.logged_in = True
            st.session_state.role = user[3]
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid login credentials")

# ---------------- STUDENT VIEW ----------------
elif st.session_state.role == "student":
    st.subheader("🧑‍🎓 Student Dashboard")

    st.info("Please answer all questions honestly.")

    st.markdown("### SECTION A: Knowledge of Sterilization")
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
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO responses (knowledge, awareness, practice) VALUES (?,?,?)",
            (knowledge, awareness, practice)
        )
        db.commit()

        st.success("Assessment submitted successfully!")

        st.markdown("### 📊 Your Results")
        st.write("Knowledge Score:", knowledge)
        st.write("Awareness Score:", awareness)
        st.write("Practice Score:", practice)

        st.info("Recommendation: Improve adherence to sterilization and infection control guidelines.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# ---------------- ADMIN VIEW ----------------
elif st.session_state.role == "admin":
    st.subheader("🧑‍💼 Admin Dashboard")

    db = get_db()
    df = pd.read_sql_query("SELECT * FROM responses", db)

    st.write("### Collected Responses")
    st.dataframe(df)

    if not df.empty:
        st.write("### 📈 Average Scores")
        averages = df[["knowledge", "awareness", "practice"]].mean()
        st.bar_chart(averages)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
