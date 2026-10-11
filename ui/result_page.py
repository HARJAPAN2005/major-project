import tkinter as tk
import os
import numpy as np
from PIL import Image, ImageTk

class ResultPage:
    def __init__(self, app, result):
        self.app = app
        self.app.root.unbind_all("<MouseWheel>")

        # ==========================================
        # SCROLLABLE FRAME SETUP
        # ==========================================
        container = app.content_frame

        canvas = tk.Canvas(container, bg="#eef6f9", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, bg="#eef6f9")

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        def resize_frame(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_frame)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mouse_wheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scrollable_frame

        # ==========================================
        # HEADER
        # ==========================================
        back_btn = tk.Button(frame, text="← Back",
                             font=("Segoe UI", 11),
                             bg="#eef6f9", fg="#1f4e79",
                             bd=0, cursor="hand2",
                             command=self.go_back)
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        tk.Label(frame, text="Clinical Analysis Results",
                 font=("Segoe UI", 26, "bold"),
                 bg="#eef6f9", fg="#1f4e79").pack(pady=5)

        tk.Label(frame, text=f"Patient ID: {app.patient_id}",
                 font=("Segoe UI", 14),
                 bg="#eef6f9").pack()

        res_color = "green" if "No" in result else "red"
        tk.Label(frame, text=result,
                 font=("Segoe UI", 22, "bold"),
                 fg=res_color, bg="#eef6f9").pack(pady=10)

        self.photos = []
        images_found = False

        # ==========================================
        # MAIN GRID
        # ==========================================
        main_container = tk.Frame(frame, bg="#eef6f9")
        main_container.pack(fill="x", expand=True, padx=20)

        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.columnconfigure(2, weight=1)

        # ==========================================
        # EYE COLUMN
        # ==========================================
        eye_col = tk.Frame(main_container, bg="#eef6f9")
        eye_col.grid(row=0, column=0, sticky="n", padx=10)

        tk.Label(eye_col, text="EYE ANALYSIS",
                 font=("Segoe UI", 12, "bold"),
                 bg="#eef6f9", fg="#34495e").pack(pady=5)

        eye_paths = [
            ("Palpebral", "temp_eye_predicted_palp.png"),
            ("Fornix", "temp_eye_predicted_fornix.png")
        ]

        eye_rgbs = []

        for title, path in eye_paths:
            if os.path.exists(path):
                images_found = True

                self.create_image_card(
                    eye_col, title, path, (160, 140), show_rgb=False
                ).pack(pady=5)

                r, g, b = self.compute_avg_rgb(path)
                eye_rgbs.append((r, g, b))

                tk.Label(eye_col,
                         text=f"{title} Avg RGB: ({r}, {g}, {b})",
                         font=("Segoe UI", 9),
                         bg="#eef6f9",
                         fg="#1f4e79").pack()

        if eye_rgbs:
            avg_r = int(np.mean([x[0] for x in eye_rgbs]))
            avg_g = int(np.mean([x[1] for x in eye_rgbs]))
            avg_b = int(np.mean([x[2] for x in eye_rgbs]))

            tk.Label(eye_col,
                     text=f"Avg RGB (Palp + Fornix): ({avg_r}, {avg_g}, {avg_b})",
                     font=("Segoe UI", 10, "bold"),
                     bg="#eef6f9",
                     fg="#1f4e79").pack(pady=10)

        # ==========================================
        # PALM COLUMN
        # ==========================================
        palm_col = tk.Frame(main_container, bg="#eef6f9")
        palm_col.grid(row=0, column=1, sticky="n", padx=10)

        tk.Label(palm_col, text="PALM ANALYSIS",
                 font=("Segoe UI", 12, "bold"),
                 bg="#eef6f9", fg="#34495e").pack(pady=5)

        palm_path = "temp_palm_isolated.png"

        if os.path.exists(palm_path):
            images_found = True

            self.create_image_card(
                palm_col, "Isolated Palm", palm_path, (260, 260), show_rgb=False
            ).pack(pady=5)

            r, g, b = self.compute_avg_rgb(palm_path)

            tk.Label(palm_col,
                     text=f"Avg RGB: ({r}, {g}, {b})",
                     font=("Segoe UI", 10, "bold"),
                     bg="#eef6f9",
                     fg="#1f4e79").pack()

        # ==========================================
        # NAIL COLUMN
        # ==========================================
        nail_col = tk.Frame(main_container, bg="#eef6f9")
        nail_col.grid(row=0, column=2, sticky="n", padx=10)

        tk.Label(nail_col, text="NAIL ANALYSIS",
                 font=("Segoe UI", 12, "bold"),
                 bg="#eef6f9", fg="#34495e").pack(pady=5)

        nail_inner_grid = tk.Frame(nail_col, bg="#eef6f9")
        nail_inner_grid.pack()

        nail_idx = 0
        nail_rgbs = []

        for i in range(10):
            n_path = f"temp_nail_isolated_{i}.png"

            if os.path.exists(n_path):
                images_found = True

                card = self.create_image_card(
                    nail_inner_grid,
                    f"Nail {nail_idx+1}",
                    n_path,
                    (80, 80)
                )

                card.grid(row=nail_idx // 2,
                          column=nail_idx % 2,
                          padx=5, pady=5)

                r, g, b = self.compute_avg_rgb(n_path)
                nail_rgbs.append((r, g, b))

                nail_idx += 1

        if nail_rgbs:
            selected = nail_rgbs[:5]

            avg_r = int(np.mean([x[0] for x in selected]))
            avg_g = int(np.mean([x[1] for x in selected]))
            avg_b = int(np.mean([x[2] for x in selected]))

            tk.Label(nail_col,
                     text=f"Avg RGB (5 Nails): ({avg_r}, {avg_g}, {avg_b})",
                     font=("Segoe UI", 10, "bold"),
                     bg="#eef6f9",
                     fg="#1f4e79").pack(pady=10)

        if not images_found:
            tk.Label(frame,
                     text="No segmentation data found.",
                     font=("Segoe UI", 12, "italic"),
                     bg="#eef6f9",
                     fg="gray").pack(pady=20)

        tk.Button(frame,
                  text="Home Screen",
                  font=("Segoe UI", 12, "bold"),
                  bg="#2c7fb8",
                  fg="white",
                  width=18,
                  command=app.show_home).pack(pady=40)

    # ==========================================
    # IMAGE CARD + RGB
    # ==========================================
    def create_image_card(self, parent, title, path, size, show_rgb=True):
        container = tk.Frame(parent, bg="#eef6f9")

        tk.Label(container, text=title,
                 font=("Segoe UI", 9, "bold"),
                 bg="#eef6f9",
                 fg="#7f8c8d").pack()

        canvas = tk.Canvas(container,
                           width=size[0],
                           height=size[1],
                           bg="white",
                           highlightthickness=1,
                           highlightbackground="#bdc3c7")
        canvas.pack()

        try:
            img = Image.open(path)
            img.thumbnail(size)

            photo = ImageTk.PhotoImage(img)
            self.photos.append(photo)

            canvas.create_image(size[0]//2,
                                size[1]//2,
                                image=photo,
                                anchor="center")

            if show_rgb:
                r, g, b = self.compute_avg_rgb(path)

                tk.Label(container,
                         text=f"RGB: ({r}, {g}, {b})",
                         font=("Segoe UI", 8),
                         bg="#eef6f9",
                         fg="#2c3e50").pack()

        except:
            pass

        return container

    # ==========================================
    # RGB CALCULATION (ALPHA CHANNEL / PIXEL PERFECT)
    # ==========================================
    def compute_avg_rgb(self, image_path):
        try:
            # 1. Open the image in RGBA mode to read the transparency data
            img = Image.open(image_path).convert("RGBA")
            arr = np.array(img, dtype=np.int32)

            # 2. Extract ONLY the pixels where the Alpha channel (index 3) is strictly solid (> 0)
            valid_pixels = arr[arr[:, :, 3] > 0]

            if len(valid_pixels) == 0:
                return (0, 0, 0)

            # 3. Calculate the average using ONLY the Red, Green, and Blue channels (indices 0, 1, 2)
            avg = np.mean(valid_pixels[:, :3], axis=0)
            
            return tuple(map(int, avg))

        except Exception as e:
            print(f"Error calculating RGB: {e}")
            return (0, 0, 0)

    def go_back(self):
        try:
            self.app.root.unbind_all("<MouseWheel>")
        except:
            pass
        self.app.go_back()