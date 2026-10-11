import tkinter as tk
import sqlite3


class SearchPatientPage:

    def __init__(self, app):

        self.app = app
        
        # --- ADDED: Clears the active patient and locks menu when entering Search ---
        app.reset_patient()
        
        frame = app.content_frame

        back_btn = tk.Button(
            frame,
            text="← Back",
            font=("Segoe UI", 11),
            bg="#eef6f9",
            fg="#1f4e79",
            bd=0,
            cursor="hand2",
            command=self.go_back
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        tk.Label(
            frame,
            text="Search Patient",
            font=("Segoe UI", 28, "bold"),
            bg="#eef6f9",
            fg="#1f4e79"
        ).pack(pady=30)

        search_frame = tk.Frame(frame, bg="#eef6f9")
        search_frame.pack(pady=20)

        self.search_entry = tk.Entry(
            search_frame,
            width=40,
            font=("Segoe UI", 12)
        )
        self.search_entry.pack(side="left", padx=10)

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_patient
        ).pack(side="left")

        self.result_frame = tk.Frame(frame, bg="#eef6f9")
        self.result_frame.pack(pady=20)

    def go_back(self):

        self.app.go_back()

    def search_patient(self):

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get()

        conn = sqlite3.connect("patients.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id,name,mobile FROM patients
        WHERE name LIKE ? OR mobile LIKE ? OR id LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))

        patients = cursor.fetchall()
        conn.close()

        for p in patients:

            btn = tk.Button(
                self.result_frame,
                text=f"ID: {p[0]} | Name: {p[1]} | Mobile: {p[2]}",
                width=60,
                anchor="w",
                command=lambda pid=p[0], name=p[1]: self.open_patient(pid, name)
            )

            btn.pack(pady=5)

    def open_patient(self, patient_id, name):

        self.app.choose_session(patient_id, name)