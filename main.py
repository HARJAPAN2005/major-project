import tkinter as tk
from PIL import Image, ImageTk
from ui.menu_bar import MenuBar
from database import init_db, create_session, get_patient_sessions, get_session_details
import io

import os
import glob

def clear_temp_images():
    files = glob.glob("temp_*")
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print("Error deleting:", f, e)

class MedicalApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Anemia Detection - Medical AI Research")
        self.root.geometry("1400x800")
        self.root.configure(bg="#eef6f9")

        self.root.minsize(1000, 600)

        self.patient_id = None
        self.patient_name = None
        self.session = None
        self.page_history = []
        self.current_view = None

        init_db()

        self.menu = MenuBar(self)

        # -------- INFO BAR --------
        self.info_frame = tk.Frame(self.root, bg="#eef6f9")
        self.info_frame.pack(fill="x")

        self.patient_label = tk.Label(
            self.info_frame,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg="#eef6f9",
            fg="#1f4e79"
        )
        self.patient_label.pack(side="right", padx=25, pady=5)

        # -------- CONTENT --------
        self.content_frame = tk.Frame(root, bg="#eef6f9")
        self.content_frame.pack(fill="both", expand=True)

        self.show_home()

    # -------- CENTER WINDOW --------
    def center_window(self, win, width, height):

        win.update_idletasks()

        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()

        x = int((screen_w - width) / 2)
        y = int((screen_h - height) / 2)

        win.geometry(f"{width}x{height}+{x}+{y}")

    # -------- UPDATE PATIENT INFO --------
    def update_patient_info(self, patient_id, name):

        self.patient_id = patient_id
        self.patient_name = name

        self.session = create_session(patient_id)

        self.patient_label.config(
            text=f"Patient ID: {patient_id} | Name: {name} | Session {self.session}"
        )

    def reset_patient(self):

        self.patient_id = None
        self.patient_name = None
        self.session = None

        self.patient_label.config(text="")
        
        # --- ADDED: Automatically disable the prediction menu when patient is cleared ---
        if hasattr(self, 'menu'):
            self.menu.disable_prediction()

    # -------- SESSION SELECTION --------
    def choose_session(self, patient_id, name):

        win = tk.Toplevel(self.root)
        win.title("Session Selection")

        win.transient(self.root)
        win.grab_set()
        win.focus_force()

        self.center_window(win, 420, 260)

        tk.Label(
            win,
            text=f"Patient: {name}",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)

        tk.Button(
            win,
            text="Create New Session",
            font=("Segoe UI", 12, "bold"),
            width=25,
            command=lambda: self.create_new_session(patient_id, name, win)
        ).pack(pady=10)

        tk.Button(
            win,
            text="Update Existing Session",
            font=("Segoe UI", 12, "bold"),
            width=25,
            command=lambda: self.show_session_list(patient_id, name, win)
        ).pack(pady=10)

    def create_new_session(self, patient_id, name, window):

        self.patient_id = patient_id
        self.patient_name = name

        self.session = create_session(patient_id)

        self.patient_label.config(
            text=f"Patient ID: {patient_id} | Name: {name} | Session {self.session}"
        )

        window.destroy()

        self.menu.enable_prediction()

        self.show_prediction()

    # -------- SESSION LIST (UPDATED UI) --------
    def show_session_list(self, patient_id, name, parent_window):

        sessions = get_session_details(patient_id)

        win = tk.Toplevel(self.root)
        win.title("Select Session")

        win.transient(self.root)
        win.grab_set()
        win.focus_force()

        self.center_window(win, 900, 550)

        tk.Label(
            win,
            text="Select Existing Session",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        container = tk.Frame(win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row = 0
        col = 0

        for s in sessions:

            session_num = s[0]
            timestamp = s[1]
            result = s[2] if s[2] else "Result Not Available"

            eye_img = s[3]
            palm_img = s[4]
            nail_img = s[5]

            # -------- CARD --------
            card = tk.Frame(scroll_frame, bg="white", bd=2, relief="ridge", width=380, height=230)
            card.grid(row=row, column=col, padx=20, pady=15)
            card.grid_propagate(False)

            header = tk.Frame(card, bg="white")
            header.pack(fill="x", padx=10, pady=5)

            tk.Label(
                header,
                text=f"Session {session_num}",
                font=("Segoe UI", 14, "bold"),
                bg="white"
            ).pack(side="left")

            tk.Label(
                header,
                text=timestamp,
                font=("Segoe UI", 10),
                bg="white"
            ).pack(side="right")

            tk.Label(
                card,
                text=f"Result: {result}",
                font=("Segoe UI", 11, "bold"),
                fg="green",
                bg="white"
            ).pack(pady=5)

            img_frame = tk.Frame(card, bg="white")
            img_frame.pack(pady=5)

            for img_data, label in zip(
                [eye_img, palm_img, nail_img],
                ["Eye", "Palm", "Nail"]
            ):

                box = tk.Frame(img_frame, bg="white")
                box.pack(side="left", padx=10)

                tk.Label(box, text=label, bg="white").pack()

                img_container = tk.Frame(box, width=90, height=90, bg="#f0f0f0")
                img_container.pack()
                img_container.pack_propagate(False)

                if img_data:

                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((85, 85))

                    photo = ImageTk.PhotoImage(img)

                    lbl = tk.Label(img_container, image=photo, bg="#f0f0f0")
                    lbl.image = photo
                    lbl.pack(expand=True)

                else:
                    tk.Label(
                        img_container,
                        text="No Image",
                        bg="#f0f0f0",
                        font=("Segoe UI", 9)
                    ).pack(expand=True)

            tk.Button(
                card,
                text="Open Session",
                command=lambda sess=session_num: self.load_existing_session(
                    patient_id, name, sess, win, parent_window
                )
            ).pack(pady=8)

            col += 1
            if col == 2:
                col = 0
                row += 1

    def load_existing_session(self, patient_id, name, session, win, parent):

        self.patient_id = patient_id
        self.patient_name = name
        self.session = session

        self.patient_label.config(
            text=f"Patient ID: {patient_id} | Name: {name} | Session {session}"
        )

        win.destroy()
        parent.destroy()

        self.menu.enable_prediction()

        self.show_prediction()

    # -------- CLEAR PAGE --------
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # -------- NAVIGATION --------
    def navigate_to(self, builder):

        if self.current_view is not None:
            self.page_history.append(self.current_view)

        self.clear_content()
        self.current_view = builder
        builder()

    def go_back(self):

        if not self.page_history:
            return

        builder = self.page_history.pop()
        self.clear_content()
        self.current_view = builder
        builder()

    # -------- PAGES --------
    def show_home(self):

        from ui.home_page import HomePage

        def build():
            self.reset_patient()
            HomePage(self)

        self.navigate_to(build)

    def show_about(self):

        from ui.about_page import AboutPage

        def build():
            AboutPage(self)

        self.navigate_to(build)

    def show_prediction(self):
        clear_temp_images()
        from ui.prediction_page import PredictionPage

        def build():
            PredictionPage(self)

        self.navigate_to(build)

    def show_patient_registration(self):

        from ui.patient_registration import PatientRegistration

        def build():
            PatientRegistration(self)

        self.navigate_to(build)

    def show_result(self, result):

        from ui.result_page import ResultPage

        def build():
            ResultPage(self, result)

        self.navigate_to(build)
    
    # Add this method inside your MedicalApp class
    def show_questionnaire(self):
        from ui.questionnaire_page import QuestionnairePage
        def build():
            QuestionnairePage(self)
        self.navigate_to(build)

if __name__ == "__main__":

    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()