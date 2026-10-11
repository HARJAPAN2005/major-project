import tkinter as tk
from tkinter import messagebox

class QuestionnairePage:
    def __init__(self, app):
        self.app = app
        self.frame = app.content_frame
        
        # --- NEW: BACK BUTTON TO REGISTRATION ---
        back_btn = tk.Button(
            self.frame, text="← Back", font=("Segoe UI", 11),
            bg="#eef6f9", fg="#1f4e79", bd=0, cursor="hand2",
            command=self.app.go_back # This uses your existing history stack
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        tk.Label(self.frame, text="Patient Medical History", bg="#eef6f9", 
                 fg="#1f4e79", font=("Segoe UI", 24, "bold")).pack(pady=20)

        # Form Container
        self.form_container = tk.Frame(self.frame, bg="white", bd=2, relief="ridge", padx=30, pady=20)
        self.form_container.pack(pady=10, fill="both", expand=True, padx=50)

        self.questions = [
            "Do you use eye drops?",
            "Any previous eye surgery?",
            "Any latest eye trauma?",
            "Hypertension (High BP)?",
            "Diabetes?",
            "Are you taking Iron medicines/supplements?"
        ]
        self.results = {}

        for q_text in self.questions:
            self.add_question_row(q_text)

        # Remarks Section
        tk.Label(self.form_container, text="Additional Remarks:", bg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 5))
        self.remarks_text = tk.Text(self.form_container, height=3, font=("Segoe UI", 11), bd=1, relief="solid")
        self.remarks_text.pack(fill="x", pady=5)

        # Submit
        tk.Button(self.frame, text="Save & Start Anemia Detection →", font=("Segoe UI", 14, "bold"), 
                  bg="#2c7fb8", fg="white", width=35, height=2, bd=0, cursor="hand2",
                  command=self.validate_and_submit).pack(pady=25)

    def add_question_row(self, q_text):
        row = tk.Frame(self.form_container, bg="white", pady=8)
        row.pack(fill="x")
        tk.Label(row, text=q_text, bg="white", font=("Segoe UI", 11), width=40, anchor="w").pack(side="left")

        var = tk.StringVar(value="None")
        detail_entry = tk.Entry(row, font=("Segoe UI", 10), width=35, bd=1, relief="solid")
        
        def on_toggle():
            if var.get() == "Yes":
                detail_entry.pack(side="right", padx=10)
            else:
                detail_entry.pack_forget()

        tk.Radiobutton(row, text="No", variable=var, value="No", bg="white", command=on_toggle).pack(side="right", padx=5)
        tk.Radiobutton(row, text="Yes", variable=var, value="Yes", bg="white", command=on_toggle).pack(side="right", padx=5)
        self.results[q_text] = {"var": var, "entry": detail_entry}

    def validate_and_submit(self):
        # 1. Check if all questions are answered
        for q, data in self.results.items():
            if data["var"].get() == "None":
                messagebox.showwarning("Incomplete", f"Please answer: {q}")
                return
        
        # 2. Prepare Data from the form
        summary = {q: (data["var"].get(), data["entry"].get() if data["var"].get() == "Yes" else "") 
                   for q, data in self.results.items()}
        remarks = self.remarks_text.get("1.0", "end-1c")

        # 3. ✅ ACTIVE DB SAVING LOGIC (Uncommented and Corrected)
        try:
            from database import save_patient_history
            save_patient_history(self.app.patient_id, self.app.session, summary, remarks)
            print(f" Medical history successfully saved for Patient {self.app.patient_id}")
        except Exception as e:
            print(f" Database Error: {e}")
            messagebox.showerror("Database Error", f"Failed to save history: {e}")
            return # Stop here if saving fails

        # 4. Proceed to Detection
        print("Starting Anemia Screening...")
        self.app.show_prediction()