import tkinter as tk
import sqlite3


class OpenPatientPage:

    def __init__(self, app):

        self.app = app
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
            text="Open Patient",
            font=("Segoe UI", 28, "bold"),
            bg="#eef6f9",
            fg="#1f4e79"
        ).pack(pady=40)

        input_frame = tk.Frame(frame, bg="#eef6f9")
        input_frame.pack(pady=20)

        tk.Label(
            input_frame,
            text="Enter Patient ID:",
            font=("Segoe UI", 12),
            bg="#eef6f9"
        ).pack(side="left", padx=10)

        self.id_entry = tk.Entry(
            input_frame,
            width=20,
            font=("Segoe UI", 12)
        )
        self.id_entry.pack(side="left")

        tk.Button(
            frame,
            text="Open",
            font=("Segoe UI", 12, "bold"),
            command=self.open_patient
        ).pack(pady=20)

    def go_back(self):

        self.app.go_back()

    def open_patient(self):

        pid = self.id_entry.get()

        conn = sqlite3.connect("patients.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM patients WHERE id=?",
            (pid,)
        )

        result = cursor.fetchone()
        conn.close()

        if result:

            name = result[0]

            self.app.choose_session(pid, name)