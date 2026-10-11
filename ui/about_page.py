import tkinter as tk

class AboutPage:

    def __init__(self, app):
        frame = app.content_frame

        heading = tk.Label(
            frame,
            text="About This Research",
            bg="#eef6f9",
            fg="#0d3b66",
            font=("Helvetica", 28, "bold")
        )
        heading.pack(pady=60)

        tk.Label(
            frame,
            text="This project uses AI and Computer Vision\n"
                 "to detect anemia using visible biomarkers\n"
                 "from eye conjunctiva, palm and nail beds.",
            bg="#eef6f9",
            font=("Helvetica", 18),
            justify="center"
        ).pack(pady=20)