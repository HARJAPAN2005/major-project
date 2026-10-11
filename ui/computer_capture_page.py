import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import io
import os
import cv2
from ui.hgb_inference import predict_hgb
from database import update_image, get_session_images, update_session_result

# ==========================================
# IMPORT FROM YOUR ML ENGINE (ALL 3 MODELS)
# ==========================================
from ui.ml_engine import (
    test_real_image_and_save, loaded_model, 
    test_nail_image_and_save, nail_model,
    test_palm_image_and_save, palm_model
)

class ComputerCapturePage:

    def __init__(self, app):
        self.app = app
        self.patient_id = app.patient_id
        self.images = {"eye": None, "palm": None, "nail": None}

        frame = app.content_frame

        # -------- SCROLLABLE + CENTERED FIX --------
        canvas = tk.Canvas(frame, bg="#eef6f9", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)

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

        # ---- Mouse Wheel Scroll (CRASH FIX APPLIED) ----
        def on_mouse_wheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception as e:
                pass 
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        # --------------------------------

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scrollable_frame
        # --------------------------------------------

        back_btn = tk.Button(
            frame, text="← Back", font=("Segoe UI", 11),
            bg="#eef6f9", fg="#1f4e79", bd=0, cursor="hand2",
            command=self.go_back
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 0))

        heading = tk.Label(
            frame, text="Anemia Detection - Upload Images",
            bg="#eef6f9", fg="#1f4e79", font=("Segoe UI", 28, "bold")
        )
        heading.pack(pady=20)

        main_frame = tk.Frame(frame, bg="#eef6f9")
        main_frame.pack(pady=20)

        # Create the 3 upload sections
        self.create_section(main_frame, "eye", 0)
        self.create_section(main_frame, "palm", 1)
        self.create_section(main_frame, "nail", 2)

        submit_btn = tk.Button(
            frame, text="Submit", font=("Segoe UI", 16, "bold"),
            bg="#2c7fb8", fg="white", width=20, height=2, bd=0,
            cursor="hand2", command=self.predict
        )
        submit_btn.pack(pady=(20, 40))

        self.load_existing_images()

    def create_section(self, parent, img_type, col):
        tk.Label(
            parent, text=f"{img_type.capitalize()} Image",
            bg="#eef6f9", font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=col, pady=(0, 10))

        box = tk.Frame(parent, width=350, height=250, bg="white", bd=3, relief="solid")
        box.grid(row=1, column=col, padx=20)
        box.pack_propagate(False)

        label = tk.Label(box, bg="white")
        label.pack(expand=True)

        tk.Button(
            parent, text="Upload Image", font=("Segoe UI", 12),
            command=lambda: self.upload_image(img_type, label)
        ).grid(row=2, column=col, pady=(15, 5))

        tk.Button(
            parent, text="Crop", font=("Segoe UI", 12),
            command=lambda: self.open_crop_window(img_type, label)
        ).grid(row=3, column=col)

        setattr(self, f"{img_type}_label", label)

    def upload_image(self, img_type, label):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path: return

        img = Image.open(file_path)
        img = ImageOps.exif_transpose(img)
        self.images[img_type] = img

        display_img = img.copy()
        display_img.thumbnail((350, 250))
        photo = ImageTk.PhotoImage(display_img)

        label.config(image=photo)
        label.image = photo

    def load_existing_images(self):
        images = get_session_images(self.patient_id, self.app.session)
        if not images: return

        for img_type, data in zip(["eye", "palm", "nail"], images):
            if data:
                img = Image.open(io.BytesIO(data))
                img = ImageOps.exif_transpose(img)
                self.images[img_type] = img # Original high-res saved safely
                
                # 🔥 FIX: Copy protects the original from getting shrunk
                display_img = img.copy()
                display_img.thumbnail((350, 250))
                photo = ImageTk.PhotoImage(display_img)

                label = getattr(self, f"{img_type}_label")
                label.config(image=photo)
                label.image = photo

    def open_crop_window(self, img_type, label):
        if self.images[img_type] is None: return

        win = tk.Toplevel(self.app.root)
        win.title("Crop Image")
        win.geometry("650x680")
        win.transient(self.app.root)
        win.grab_set()

        img_original = self.images[img_type]
        canvas_w = 500
        canvas_h = 380

        canvas = tk.Canvas(win, width=canvas_w, height=canvas_h, bg="black")
        canvas.pack(pady=10)

        img_w, img_h = img_original.size
        scale = min(canvas_w / img_w, canvas_h / img_h)

        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)
        display = img_original.resize((disp_w, disp_h))
        tk_img = ImageTk.PhotoImage(display)

        offset_x = (canvas_w - disp_w) // 2
        offset_y = (canvas_h - disp_h) // 2

        canvas.create_image(offset_x, offset_y, anchor="nw", image=tk_img)
        canvas.image = tk_img

        control = tk.Frame(win)
        control.pack(pady=10)

        tk.Label(control, text="Aspect Ratio").pack()
        ratio_var = tk.StringVar(value="3:4")
        ratio_menu = tk.OptionMenu(control, ratio_var, "4:3", "3:4", "1:1", "16:9", "9:16")
        ratio_menu.pack(pady=5)

        tk.Label(control, text="Frame Size").pack()
        size_var = tk.IntVar(value=200)
        tk.Scale(control, from_=80, to=350, orient="horizontal", variable=size_var).pack()

        self.center_x = canvas_w // 2
        self.center_y = canvas_h // 2

        rect = canvas.create_rectangle(150, 100, 350, 300, outline="red", width=2)

        def update_rect():
            try:
                rw, rh = map(float, ratio_var.get().split(":"))
            except:
                rw = rh = 1.0

            size = size_var.get()
            w = size
            h = int(size * rh / rw)
            x1 = self.center_x - w // 2
            y1 = self.center_y - h // 2
            x2 = self.center_x + w // 2
            y2 = self.center_y + h // 2

            canvas.coords(rect, x1, y1, x2, y2)

        def move_rect(event):
            self.center_x = event.x
            self.center_y = event.y
            update_rect()

        canvas.bind("<B1-Motion>", move_rect)
        canvas.bind("<Button-1>", move_rect)
        size_var.trace_add("write", lambda *args: update_rect())
        ratio_var.trace_add("write", lambda *args: update_rect())
        update_rect()

        def finish():
            x1, y1, x2, y2 = canvas.coords(rect)
            x1 -= offset_x
            x2 -= offset_x
            y1 -= offset_y
            y2 -= offset_y

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(disp_w, x2)
            y2 = min(disp_h, y2)

            scale_back = 1 / scale
            crop = img_original.crop((
                int(x1 * scale_back), int(y1 * scale_back),
                int(x2 * scale_back), int(y2 * scale_back)
            ))

            self.images[img_type] = crop

            display_crop = crop.copy()
            display_crop.thumbnail((350, 250))
            photo = ImageTk.PhotoImage(display_crop)

            label.config(image=photo)
            label.image = photo
            win.destroy()

        tk.Button(
            win, text="Done", font=("Segoe UI", 12, "bold"),
            bg="#2c7fb8", fg="white", command=finish
        ).pack(pady=10)

    def predict(self):
        # 1. Save original inputs
        for img_type in ["eye", "palm", "nail"]:
            if self.images[img_type]:
                temp = f"temp_{img_type}.png"
                self.images[img_type].save(temp)
                update_image(self.patient_id, self.app.session, img_type, temp)

        # ==========================================
        # 2. RUN EYE SEGMENTATION FIRST
        # ==========================================
        eye_success = False
        if self.images["eye"] and loaded_model is not None:
            print("Running AI model via ml_engine for EYE...")
            forn_img, palp_img = test_real_image_and_save("temp_eye.png", loaded_model)
            
            if forn_img is not None and palp_img is not None:
                # 🔥 KEEP TRANSPARENCY: Saved as BGRA for the UI, model handles it later
                save_fornix = cv2.cvtColor(forn_img, cv2.COLOR_RGBA2BGRA)
                save_palp = cv2.cvtColor(palp_img, cv2.COLOR_RGBA2BGRA)
                
                cv2.imwrite("temp_eye_predicted_fornix.png", save_fornix)
                cv2.imwrite("temp_eye_predicted_palp.png", save_palp)
                print("✅ Isolated eye segments generated and saved as transparent PNGs!")
                eye_success = True

        # ==========================================
        # 3. RUN PALM MODEL
        # ==========================================
        if self.images["palm"] and palm_model is not None:
            print("Running AI model via ml_engine for PALM...")
            palm_img = test_palm_image_and_save("temp_palm.png", palm_model)
            
            if palm_img is not None:
                save_palm = cv2.cvtColor(palm_img, cv2.COLOR_RGBA2BGRA)
                cv2.imwrite("temp_palm_isolated.png", save_palm)
                print("✅ Isolated palm segment generated and saved!")
            else:
                print("⚠️ Palm model ran, but no hand was detected.")

        # ==========================================
        # 4. RUN NAIL MODEL
        # ==========================================
        for i in range(10):
            if os.path.exists(f"temp_nail_isolated_{i}.png"):
                os.remove(f"temp_nail_isolated_{i}.png")

        if self.images["nail"] and nail_model is not None:
            print("Running AI model via ml_engine for NAILS...")
            nail_images = test_nail_image_and_save("temp_nail.png", nail_model)
            
            if nail_images:
                for idx, n_img in enumerate(nail_images):
                    save_nail = cv2.cvtColor(n_img, cv2.COLOR_RGBA2BGRA)
                    cv2.imwrite(f"temp_nail_isolated_{idx}.png", save_nail)
                print(f"✅ {len(nail_images)} isolated nail segments generated and saved!")
            else:
                print("⚠️ Nail model ran, but no nails were detected above the threshold.")

        # ==========================================
        # 5. RUN Hb PREDICTION SECOND
        # ==========================================
        final_result = "No Anemia Detected" # Default fallback
        
        if eye_success:
            try:
                print("🚀 Running Deep Learning Hb Inference...")
                # Pass BOTH arguments here AFTER segmentation is done
                hb_value = predict_hgb("temp_eye_predicted_fornix.png", "temp_eye_predicted_palp.png")
                print(f"🩸 Hb: {hb_value:.2f}")

                # Format the text so the Result Page can color-code it
                if hb_value < 10:
                    final_result = f"⚠️ Likely Anemia (Hb: {hb_value:.2f} g/dL)"
                elif hb_value < 12:
                    final_result = f"⚠️ Borderline (Hb: {hb_value:.2f} g/dL)"
                else:
                    final_result = f"✅ No Anemia (Hb: {hb_value:.2f} g/dL)"

            except Exception as e:
                print("Hb Error:", e)
                final_result = "Hb Prediction Failed"

        # ------------------------------------------
        # 6. FINAL RESULT LOGIC
        # ------------------------------------------
        update_session_result(self.patient_id, self.app.session, final_result)
        self.app.show_result(final_result)
        
    def go_back(self):
        canvas = self.app.content_frame.winfo_children()[0]
        canvas.unbind_all("<MouseWheel>")
        self.app.go_back()