import sqlite3
import os
from PIL import Image
from datetime import datetime

def init_db():
    # Adding timeout=10 to help prevent "database is locked" errors during manual testing
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()

    # CRITICAL: Enable Foreign Key support in SQLite (it is off by default)
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Create Patients Table (The Parent Table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        mobile TEXT,
        email TEXT
    )
    """)

    # 2. Create Sessions Table (The Child Table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        session INTEGER,
        eye_image BLOB,
        palm_image BLOB,
        nail_image BLOB,
        result TEXT,
        timestamp TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    # 3. Create History Table (The Child Table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        session INTEGER,
        question TEXT,
        answer TEXT,
        details TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    # Handle the Alter Table for older DB versions
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN result TEXT")
    except sqlite3.OperationalError:
        pass

    # ✅ AUTO-RESET COUNTER LOGIC
    cursor.execute("SELECT MAX(id) FROM patients")
    max_id = cursor.fetchone()[0]
    new_seq = max_id if max_id is not None else 0
    
    cursor.execute("INSERT OR IGNORE INTO sqlite_sequence (name, seq) VALUES ('patients', 0)")
    cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'patients'", (new_seq,))

    conn.commit()
    conn.close()
    print(f"✅ Database synced. Next Patient ID will be {new_seq + 1}. Referential Integrity Active.")

def insert_patient(name, dob, gender, address, mobile, email):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO patients(name,dob,gender,address,mobile,email)
    VALUES(?,?,?,?,?,?)
    """, (name, dob, gender, address, mobile, email))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def create_session(patient_id):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(session) FROM sessions WHERE patient_id=?", (patient_id,))
    result = cursor.fetchone()[0]
    session = 1 if result is None else result + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO sessions(patient_id,session,timestamp)
    VALUES(?,?,?)
    """, (patient_id, session, timestamp))
    conn.commit()
    conn.close()
    return session

def save_patient_history(patient_id, session, history_data, remarks):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    
    for q_text, data in history_data.items():
        ans = data[0]
        details = data[1]
        cursor.execute("""
        INSERT INTO history(patient_id, session, question, answer, details)
        VALUES(?,?,?,?,?)
        """, (patient_id, session, q_text, ans, details))
    
    if remarks.strip():
        cursor.execute("""
        INSERT INTO history(patient_id, session, question, answer, details)
        VALUES(?,?,?,?,?)
        """, (patient_id, session, "Additional Remarks", "Note", remarks))
        
    conn.commit()
    conn.close()
    print(f"✅ History saved for ID: {patient_id}")

def update_image(patient_id, session, column, file_path):
    base = "database_images"
    os.makedirs(base, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{patient_id}_s{session}_{column}_{timestamp}.jpg"
    save_path = os.path.join(base, filename)

    img = Image.open(file_path).convert("RGB")
    img.save(save_path, format="JPEG")

    with open(save_path, "rb") as f:
        binary_data = f.read()

    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    query = f"UPDATE sessions SET {column}_image=? WHERE patient_id=? AND session=?"
    cursor.execute(query, (binary_data, patient_id, session))
    conn.commit()
    conn.close()
    return save_path

def update_session_result(patient_id, session, result_text):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET result=? WHERE patient_id=? AND session=?", 
                   (result_text, patient_id, session))
    conn.commit()
    conn.close()

# ✅ RE-ADDED: This function was missing and causing your crash
def get_patient_sessions(patient_id):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT session, timestamp, result 
    FROM sessions 
    WHERE patient_id=? 
    ORDER BY session DESC
    """, (patient_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_details(patient_id):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT session, timestamp, result, eye_image, palm_image, nail_image
    FROM sessions WHERE patient_id=? ORDER BY session DESC
    """, (patient_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_images(patient_id, session):
    conn = sqlite3.connect("patients.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT eye_image, palm_image, nail_image FROM sessions WHERE patient_id=? AND session=?", 
                   (patient_id, session))
    data = cursor.fetchone()
    conn.close()
    return data