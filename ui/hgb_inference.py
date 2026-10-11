import torch
import numpy as np
import pandas as pd
import cv2

from src.config import DEVICE
from src.model import HbDualModel

# 🔥 WE NOW DIRECTLY IMPORT YOUR EXACT TRAINING FUNCTIONS
from src.utils import get_original_color_image, extract_roi, to_lab_tensor

# =====================================
# LOAD MODEL & STATS
# =====================================
model = HbDualModel().to(DEVICE)
checkpoint = torch.load("best_model.pth", map_location=DEVICE)

if isinstance(checkpoint, dict) and "model" in checkpoint:
    model.load_state_dict(checkpoint["model"])
else:
    model.load_state_dict(checkpoint)

df = pd.read_excel("Sample.xlsx")
df["Hgb"] = pd.to_numeric(df["Hgb"], errors="coerce")
mean, std = df["Hgb"].mean(), df["Hgb"].std()

model.eval()

# =====================================
# MAIN INFERENCE FUNCTION
# =====================================
def predict_hgb(fornix_path, palpebral_path):
    # 1. EXACT logic from ItalyDataset __getitem__
    f_raw = get_original_color_image(fornix_path)
    p_raw = get_original_color_image(palpebral_path)

    f_img = extract_roi(f_raw)
    p_img = extract_roi(p_raw)

    # 2. EXACT Resize to 256x256 from ItalyDataset
    f_img = cv2.resize(f_img, (256, 256))
    p_img = cv2.resize(p_img, (256, 256))

    # 3. EXACT Feature Extraction from ItalyDataset
    lab_f = cv2.cvtColor(f_img, cv2.COLOR_RGB2LAB)
    lab_p = cv2.cvtColor(p_img, cv2.COLOR_RGB2LAB)

    A_mean = ((lab_f[:, :, 1].mean() + lab_p[:, :, 1].mean()) / 2) / 255.0
    R_mean = (f_img[:, :, 0].mean() + p_img[:, :, 0].mean()) / 2
    G_mean = (f_img[:, :, 1].mean() + p_img[:, :, 1].mean()) / 2

    rg_ratio = (R_mean / (G_mean + 1e-6)) / 2.0

    extra = torch.tensor([[A_mean, rg_ratio]]).float().to(DEVICE)

    # 4. EXACT Tensor conversion using your utils.py
    f = to_lab_tensor(f_img).unsqueeze(0).to(DEVICE)
    p = to_lab_tensor(p_img).unsqueeze(0).to(DEVICE)

    # 5. EXACT TTA (Test-Time Augmentation) from your predict_all_patients code
    with torch.no_grad():
        preds_aug = []
        for flip in [False, True]:
            if flip:
                f_aug = torch.flip(f, [3])
                p_aug = torch.flip(p, [3])
            else:
                f_aug, p_aug = f, p

            pred, _, _ = model(f_aug, p_aug, extra)
            preds_aug.append(pred.cpu().numpy()[0][0])

        pred_val = np.mean(preds_aug)

    # 6. EXACT De-normalize & Calibration from predict_all_patients
    pred_hb = pred_val * std + mean
    pred_hb = 0.85 * pred_hb + 0.15 * mean  # Calibration line

    return pred_hb