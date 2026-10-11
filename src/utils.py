import cv2
import numpy as np


def get_original_color_image(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if len(img.shape) == 3 and img.shape[2] == 4:
        img_rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        rgb = img_rgba[:, :, :3]
        alpha = img_rgba[:, :, 3] / 255.0
        return (rgb * alpha[:, :, None]).astype(np.uint8)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_rgb[gray > 240] = [0, 0, 0]
    return img_rgb


# 🔥 BEST ROI (adaptive)
def extract_roi(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    A = lab[:, :, 1]

    thresh = np.percentile(A, 75)

    mask = (A > thresh).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (9, 9), 0)

    mask = np.expand_dims(mask, axis=2)

    enhanced = img * (0.4 + 1.4 * mask)

    return np.clip(enhanced, 0, 255).astype(np.uint8)


def to_lab_tensor(img):
    img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
    img_lab[:, :, 0] /= 100.0
    img_lab[:, :, 1] = (img_lab[:, :, 1] + 128) / 255.0
    img_lab[:, :, 2] = (img_lab[:, :, 2] + 128) / 255.0

    import torch
    return torch.tensor(img_lab).permute(2, 0, 1)