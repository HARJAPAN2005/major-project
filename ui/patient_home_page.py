import tkinter as tk



class HomePage:



    def __init__(self, app):

        frame = app.content_frame



        back_btn = tk.Button(

            frame,

            text="← Back",

            font=("Helvetica", 11),

            bg="#eef6f9",

            fg="#0d3b66",

            bd=0,

            cursor="hand2",

            command=app.go_back

        )

        back_btn.pack(anchor="w", padx=20, pady=(10, 0))



        heading = tk.Label(

            frame,

            text="Anemia Detection using Eyes, Palm & Nail",

            bg="#eef6f9",

            fg="#0d3b66",

            font=("Helvetica", 32, "bold")

        )

        heading.pack(pady=80)



        sub_text = tk.Label(

            frame,

            text="AI-powered non-invasive screening system\nfor early anemia detection.",

            bg="#eef6f9",

            fg="#333333",

            font=("Helvetica", 18)

        )

        sub_text.pack(pady=10)



        proceed_btn = tk.Button(

            frame,

            text="Proceed for Anemia Detection",

            font=("Helvetica", 18, "bold"),

            bg="#1b98e0",

            fg="white",

            padx=40,

            pady=15,

            bd=0,

            cursor="hand2",

            command=app.show_prediction

        )

        proceed_btn.pack(pady=60)