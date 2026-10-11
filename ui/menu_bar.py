import tkinter as tk


class MenuBar:

    def __init__(self, app):

        self.app = app

        self.menu_frame = tk.Frame(app.root, bg="#0d3b66", height=60)
        self.menu_frame.pack(fill="x")

        # ---------- LEFT MENU ----------
        left_frame = tk.Frame(self.menu_frame, bg="#0d3b66")
        left_frame.pack(side="left", padx=20)

        # ---------------- HOME ----------------
        home_btn = tk.Button(
            left_frame,
            text="Home",
            bg="#0d3b66",
            fg="white",
            font=("Helvetica", 14),
            bd=0,
            cursor="hand2",
            command=app.show_home
        )
        home_btn.pack(side="left", padx=10)

        # ---------------- FILE MENU ----------------
        self.file_btn = tk.Menubutton(
            left_frame,
            text="File ▾",
            bg="#0d3b66",
            fg="white",
            font=("Helvetica", 14),
            bd=0,
            activebackground="#145da0",
            activeforeground="white",
            cursor="hand2"
        )
        self.file_btn.pack(side="left", padx=10)

        file_menu = tk.Menu(self.file_btn, tearoff=0)
        self.file_btn.config(menu=file_menu)

        file_menu.add_command(
            label="New Patient Registration",
            command=self.new_patient
        )

        file_menu.add_command(
            label="Open Patient",
            command=self.open_patient
        )

        file_menu.add_command(
            label="Search Patient",
            command=self.search_patient
        )

        # ---------------- ANEMIA PREDICTION MENU ----------------
        self.pred_btn = tk.Menubutton(
            left_frame,
            text="Anemia Prediction ▾",
            bg="#0d3b66",
            fg="white",
            font=("Helvetica", 14),
            bd=0,
            activebackground="#145da0",
            activeforeground="white",
            cursor="hand2"
        )
        self.pred_btn.pack(side="left", padx=10)

        pred_menu = tk.Menu(self.pred_btn, tearoff=0)
        self.pred_btn.config(menu=pred_menu)

        pred_menu.add_command(
            label="Computer Image Capture",
            command=self.computer_capture
        )

        # ---------------- ABOUT ----------------
        about_btn = tk.Button(
            left_frame,
            text="About",
            bg="#0d3b66",
            fg="white",
            font=("Helvetica", 14),
            bd=0,
            cursor="hand2",
            command=app.show_about
        )
        about_btn.pack(side="left", padx=10)

        # disable prediction initially
        self.disable_prediction()

    # ---------------- MENU CONTROL ----------------

    def disable_prediction(self):
        self.pred_btn.config(state="disabled")

    def enable_prediction(self):
        self.pred_btn.config(state="normal")

    # ---------------- FILE MENU ----------------

    def new_patient(self):

        # reset patient info
        self.app.reset_patient()

        # disable prediction again
        self.disable_prediction()

        self.app.show_patient_registration()

    def open_patient(self):
        from ui.open_patient_page import OpenPatientPage
        self.app.navigate_to(lambda: OpenPatientPage(self.app))

    def search_patient(self):
        from ui.search_patient_page import SearchPatientPage
        self.app.navigate_to(lambda: SearchPatientPage(self.app))

    # ---------------- PREDICTION ----------------

    def computer_capture(self):

        from ui.computer_capture_page import ComputerCapturePage

        if self.app.patient_id is None:
            print("Register patient first")
            return

        self.app.clear_content()
        ComputerCapturePage(self.app)