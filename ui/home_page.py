import tkinter as tk


class HomePage:

    def __init__(self, app):

        frame = app.content_frame

        main = tk.Frame(frame, bg="#eef6f9")
        main.pack(fill="both", expand=True)

        # -------- HERO SECTION --------
        hero = tk.Frame(main, bg="#eef6f9")
        hero.pack(pady=25)

        tk.Label(
            hero,
            text="AI-Based Anemia Detection System",
            font=("Segoe UI", 34, "bold"),
            bg="#eef6f9",
            fg="#0d3b66"
        ).pack(pady=5)

        tk.Label(
            hero,
            text="Non-Invasive Screening using Eye, Palm and Nail Images",
            font=("Segoe UI", 15),
            bg="#eef6f9",
            fg="#444444"
        ).pack()

        # -------- FEATURE CARDS --------
        card_frame = tk.Frame(main, bg="#eef6f9")
        card_frame.pack(pady=30)

        self.create_card(
            card_frame,
            "👁 Eye Analysis",
            "Detect pallor in conjunctiva\nfor early anemia indication",
            0
        )

        self.create_card(
            card_frame,
            "✋ Palm Analysis",
            "Analyze palm coloration\nfor hemoglobin estimation",
            1
        )

        self.create_card(
            card_frame,
            "💅 Nail Analysis",
            "Nail bed color detection\nfor anemia screening",
            2
        )

        # -------- ACTION BUTTON --------
        action = tk.Frame(main, bg="#eef6f9")
        action.pack(pady=25)

        tk.Button(
            action,
            text="Register New Patient",
            font=("Segoe UI", 18, "bold"),
            bg="#1b98e0",
            fg="white",
            padx=40,
            pady=12,
            bd=0,
            cursor="hand2",
            command=app.show_patient_registration
        ).pack()

        # -------- FOOTER --------
        tk.Label(
            main,
            text="Research Project • AI Powered Medical Screening",
            font=("Segoe UI", 11),
            bg="#eef6f9",
            fg="#777777"
        ).pack(side="bottom", pady=10)

    def create_card(self, parent, title, description, col):

        card = tk.Frame(
            parent,
            bg="white",
            width=280,
            height=170,
            bd=2,
            relief="ridge"
        )
        card.grid(row=0, column=col, padx=25)

        card.grid_propagate(False)

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#0d3b66"
        ).pack(pady=12)

        tk.Label(
            card,
            text=description,
            font=("Segoe UI", 11),
            bg="white",
            fg="#555555",
            justify="center"
        ).pack()