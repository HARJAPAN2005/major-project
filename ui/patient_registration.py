import tkinter as tk
from tkinter import ttk, messagebox
from database import insert_patient
from datetime import datetime


class PatientRegistration:

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

        title = tk.Label(
            frame,
            text="New Patient Registration",
            font=("Segoe UI", 30, "bold"),
            bg="#eef6f9",
            fg="#1f4e79"
        )
        title.pack(pady=20)

        form_frame = tk.Frame(frame, bg="#eef6f9")
        form_frame.pack(pady=20)

        label_style = {
            "font": ("Segoe UI", 12),
            "bg": "#eef6f9"
        }

        entry_width = 30

        # ---------------- Name ----------------
        tk.Label(form_frame, text="Name", **label_style)\
            .grid(row=0, column=0, pady=12, sticky="w")

        self.name_entry = tk.Entry(
            form_frame,
            width=entry_width,
            font=("Segoe UI", 12)
        )
        self.name_entry.grid(row=0, column=1, pady=12)

        # ---------------- DOB ----------------
        tk.Label(form_frame, text="Date of Birth", **label_style)\
            .grid(row=1, column=0, pady=12, sticky="w")

        dob_frame = tk.Frame(form_frame, bg="#eef6f9")
        dob_frame.grid(row=1, column=1, pady=12, sticky="w")

        # Day
        self.day = ttk.Combobox(
            dob_frame,
            values=list(range(1, 32)),
            width=5,
            state="readonly",
            font=("Segoe UI", 11)
        )
        self.day.pack(side="left", padx=3)

        # Month
        months = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]

        self.month = ttk.Combobox(
            dob_frame,
            values=months,
            width=10,
            state="readonly",
            font=("Segoe UI", 11)
        )
        self.month.pack(side="left", padx=3)

        # Year
        current_year = datetime.now().year
        years = list(range(1950, current_year + 1))

        self.year = ttk.Combobox(
            dob_frame,
            values=years,
            width=6,
            state="readonly",
            font=("Segoe UI", 11)
        )
        self.year.pack(side="left", padx=3)

        self.day.current(0)
        self.month.current(0)
        self.year.current(len(years)-1)

        # ---------------- Gender ----------------
        tk.Label(form_frame, text="Gender", **label_style)\
            .grid(row=2, column=0, pady=12, sticky="w")

        self.gender = ttk.Combobox(
            form_frame,
            values=["Male", "Female", "Other"],
            width=entry_width-2,
            font=("Segoe UI", 12),
            state="readonly"
        )

        self.gender.grid(row=2, column=1, pady=12)
        self.gender.current(0)

        # ---------------- Address ----------------
        tk.Label(form_frame, text="Address", **label_style)\
            .grid(row=3, column=0, pady=12, sticky="w")

        self.address_entry = tk.Entry(
            form_frame,
            width=entry_width,
            font=("Segoe UI", 12)
        )

        self.address_entry.grid(row=3, column=1, pady=12)

        # ---------------- Mobile ----------------
        tk.Label(form_frame, text="Mobile", **label_style)\
            .grid(row=4, column=0, pady=12, sticky="w")

        self.mobile_entry = tk.Entry(
            form_frame,
            width=entry_width,
            font=("Segoe UI", 12)
        )

        self.mobile_entry.grid(row=4, column=1, pady=12)

        # ---------------- Email ----------------
        tk.Label(form_frame, text="Email", **label_style)\
            .grid(row=5, column=0, pady=12, sticky="w")

        self.email_entry = tk.Entry(
            form_frame,
            width=entry_width,
            font=("Segoe UI", 12)
        )

        self.email_entry.grid(row=5, column=1, pady=12)

        # ---------------- Register Button ----------------
        register_btn = tk.Button(
            frame,
            text="Register & Continue",
            font=("Segoe UI", 14, "bold"),
            bg="#2c7fb8",
            fg="white",
            padx=40,
            pady=5,
            cursor="hand2",
            command=self.register_patient
        )

        register_btn.pack(pady=25)

    # ---------------- Register Function ----------------
    def go_back(self):
        self.app.go_back()

    # ---------------- Register Function ----------------
    def register_patient(self):

        name = self.name_entry.get()

        dob = f"{self.day.get()} {self.month.get()} {self.year.get()}"

        gender = self.gender.get()
        address = self.address_entry.get()
        mobile = self.mobile_entry.get()
        email = self.email_entry.get()

        # ✅ FUTURE DATE VALIDATION (ADDED)
        try:
            selected_date = datetime.strptime(dob, "%d %B %Y")
            if selected_date > datetime.today():
                messagebox.showerror(
                    "Invalid Date of Birth",
                    "Date of Birth cannot be in the future."
                )
                return
        except:
            messagebox.showerror(
                "Invalid Date",
                "Please select a valid date."
            )
            return

        # Basic validation for mobile number
        mobile_clean = mobile.strip()
        if not mobile_clean.isdigit() or len(mobile_clean) != 10:
            messagebox.showerror(
                "Invalid Mobile Number",
                "Please enter a valid 10-digit mobile number."
            )
            return

        # Basic validation for email format
        email_clean = email.strip()
        if "@" not in email_clean or "." not in email_clean.split("@")[-1]:
            messagebox.showerror(
                "Invalid Email",
                "Please enter a valid email address (e.g., user@example.com)."
            )
            return

        patient_id = insert_patient(
            name,
            dob,
            gender,
            address,
            mobile,
            email
        )

        self.app.update_patient_info(patient_id, name)
        self.app.menu.enable_prediction()

        print("Patient Registered with ID:", patient_id)

        # ✅ SEQUENTIAL WORKFLOW: Navigate to Questionnaire
        self.app.show_questionnaire()