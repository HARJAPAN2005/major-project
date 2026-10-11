import tkinter as tk


class PredictionPage:

    def __init__(self, app):

        self.app = app

        frame = app.content_frame

        back_btn = tk.Button(
            frame,
            text="← Back",
            font=("Segoe UI", 11),
            bg="#eef6f9",
            fg="#1f4e79",
            bd=0,
            cursor="hand2",
            command=app.go_back
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        heading = tk.Label(
            frame,
            text="Anemia Detection",
            bg="#eef6f9",
            fg="#1f4e79",
            font=("Segoe UI", 30, "bold")
        )
        heading.pack(pady=40)

        button_frame = tk.Frame(frame, bg="#eef6f9")
        button_frame.pack(pady=15)

        # -------- Computer Capture Button --------
        computer_btn = tk.Button(
            button_frame,
            text="Computer Image Capture",
            font=("Segoe UI", 16, "bold"),
            bg="#2c7fb8",
            fg="white",
            width=25,
            pady=12,
            cursor="hand2",
            command=self.computer_capture
        )
        computer_btn.pack(pady=15)


    def computer_capture(self):

        from ui.computer_capture_page import ComputerCapturePage

        self.app.navigate_to(lambda: ComputerCapturePage(self.app))