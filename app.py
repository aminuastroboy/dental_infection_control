import streamlit as st
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import os

st.set_page_config(page_title="Dental Infection Control System", layout="centered")

# ---------------- DATABASE INITIALIZATION ----------------
DB_PATH = os.path.join(os.getcwd(), "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Responses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        knowledge INTEGER,
        awareness INTEGER,
        practice INTEGER
    )
    """)

    # Insert default admin if not exists
    cur.execute("SELECT * FROM users WHERE email=?", ("admin@test.com",))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (email, password, role) VALUES (?,?,?)",
                    ("admin@test.com", generate_password_hash("admin123"), "admin"))

    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

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
            st.stop()
else:
    
