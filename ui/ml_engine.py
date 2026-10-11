import os
import cv2
import numpy as np
import tensorflow as tf
import torch
from PIL import Image

# ==========================================
# 0. TENSORFLOW SAFE MODE & DEVICE CONFIG
# ==========================================
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Define device globally
pytorch_device = "cuda" if torch.cuda.is_available() else "cpu"

# ==========================================
# 1. LOAD TENSORFLOW EYE MODEL
# ==========================================
class_weights = tf.constant([0.2, 0.4, 0.4], dtype=tf.float32)

def dice_loss(y_true, y_pred, smooth=1e-6):
    y_true = tf.cast(tf.one_hot(tf.cast(y_true, tf.int32), depth=3), tf.float32)
    y_pred = tf.nn.softmax(y_pred, axis=-1)
    intersection = tf.reduce_sum(y_true * y_pred, axis=[1,2])
    union = tf.reduce_sum(y_true + y_pred, axis=[1,2])
    return 1 - tf.reduce_mean((2. * intersection + smooth) / (union + smooth))

def weighted_sparse_ce(y_true, y_pred):
    y_true = tf.cast(y_true, tf.int32)
    weights = tf.gather(class_weights, y_true)
    ce = tf.keras.losses.sparse_categorical_crossentropy(y_true, y_pred, from_logits=True)
    return tf.reduce_mean(ce * weights)

def combined_loss(y_true, y_pred):
    return weighted_sparse_ce(y_true, y_pred) + dice_loss(y_true, y_pred)

print("Waking up the MobileNetV2 EyeDefy model...")
try:
    EYE_MODEL_PATH = os.path.join(parent_dir, "eyedefy_mobilenet_unet.keras")
    loaded_model = tf.keras.models.load_model(
        EYE_MODEL_PATH,
        custom_objects={
            "combined_loss": combined_loss,
            "dice_loss": dice_loss,
            "weighted_sparse_ce": weighted_sparse_ce
        },
        safe_mode=False
    )
    print("✅ Eye Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Eye Model failed to load: {e}")
    loaded_model = None

# ==========================================
# 2. LOAD PYTORCH NAIL MODEL
# ==========================================
print("Waking up PyTorch Nail model...")
try:
    from ui.model import AttentionUNet
    NAIL_MODEL_PATH = os.path.join(parent_dir, "nail_segmentation.pth")
    nail_model = AttentionUNet().to(pytorch_device)
    nail_model.load_state_dict(torch.load(NAIL_MODEL_PATH, map_location=pytorch_device, weights_only=True))
    nail_model.eval()
    print("✅ Nail Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Nail Model failed to load: {e}")
    nail_model = None

# ==========================================
# 2.5 LOAD PYTORCH PALM MODEL (U2-NET)
# ==========================================
print("Waking up PyTorch Palm model (U2-Net)...")
try:
    from ui.u2net import U2NET
    PALM_MODEL_PATH = os.path.join(parent_dir, "u2net.pth")
    palm_model = U2NET(3, 1).to(pytorch_device)
    palm_model.load_state_dict(torch.load(PALM_MODEL_PATH, map_location=pytorch_device, weights_only=True))
    palm_model.eval()
    print("✅ Palm Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Palm Model failed to load: {e}")
    palm_model = None

# ==========================================
# 3. EYE PROCESSING PIPELINE
# ==========================================
def clean_prediction_mask(pred_mask):
    cleaned_mask = np.zeros_like(pred_mask, dtype=np.uint8)
    for class_id in [1, 2]:
        binary_mask = np.uint8(pred_mask == class_id) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
        if num_labels > 1:
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            cleaned_mask[labels == largest_label] = class_id
    return cleaned_mask

def test_real_image_and_save(image_path, model, IMG_SIZE=128):
    if model is None: return None, None
    orig_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if orig_img is None: return None, None

    orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
    h, w = orig_img.shape[:2]
    size = min(h, w)
    y1, x1 = (h - size) // 2, (w - size) // 2
    cropped_img = orig_img[y1:y1+size, x1:x1+size]

    img_norm = cv2.resize(cropped_img, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
    pred = model.predict(np.expand_dims(img_norm, axis=0), verbose=0)
    clean_mask_128 = clean_prediction_mask(np.argmax(pred[0], axis=-1).astype(np.uint8))
    final_mask = cv2.resize(clean_mask_128, (size, size), interpolation=cv2.INTER_NEAREST)

    fornix_segment = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2RGBA)
    fornix_segment[final_mask != 1, 3] = 0 

    palp_segment = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2RGBA)
    palp_segment[final_mask != 2, 3] = 0 

    return fornix_segment, palp_segment

# ==========================================
# 4. NAIL PROCESSING (FIXED: CONSISTENCY)
# ==========================================
def test_nail_image_and_save(image_path, model, THRESH=0.12, MIN_AREA=80):
    if model is None: return None

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None: return None

    H, W = img.shape[:2]
    inp = cv2.resize(img, (256, 256)) / 255.0
    tensor = torch.tensor(inp).permute(2,0,1).unsqueeze(0).float().to(pytorch_device)

    with torch.no_grad():
        pred = model(tensor)[0,0].cpu().numpy()

    pred = cv2.resize(pred, (W,H))
    # 🔥 Lowered Threshold for better detection in varied lighting
    mask = (pred > THRESH).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    isolated_nails = []
    
    for c in contours:
        # 🔥 Lowered Min Area for further-away hands
        if cv2.contourArea(c) < MIN_AREA: continue

        x, y, wc, hc = cv2.boundingRect(c)
        # Added small 5px padding
        y1, x1 = max(0, y-5), max(0, x-5)
        y2, x2 = min(H, y+hc+5), min(W, x+wc+5)
        
        nail_crop = img[y1:y2, x1:x2]
        nail_mask = mask[y1:y2, x1:x2]

        shaped_rgba = cv2.cvtColor(nail_crop, cv2.COLOR_BGR2BGRA)
        shaped_rgba[nail_mask == 0, 3] = 0 

        if shaped_rgba.size > 0:
            isolated_nails.append(cv2.cvtColor(shaped_rgba, cv2.COLOR_BGRA2RGBA))

    return isolated_nails

# ==========================================
# 5. PALM PROCESSING (FIXED: SEGMENTATION)
# ==========================================
def test_palm_image_and_save(image_path, model, IMG_SIZE=320):
    if model is None: return None
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None: return None
    
    h, w = img.shape[:2]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    inp = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE)) / 255.0
    inp = inp.transpose(2, 0, 1)
    inp = torch.tensor(inp, dtype=torch.float32).unsqueeze(0).to(pytorch_device)

    with torch.no_grad():
        d1, *_ = model(inp)
        pred = torch.sigmoid(d1)[0, 0].cpu().numpy()

    # 🔥 DYNAMIC NORMALIZATION: Fixes thresholding issues in old/dark sessions
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    
    # 0.4 Threshold is more forgiving than 0.5
    mask = (pred > 0.4).astype(np.uint8) * 255
    mask = cv2.resize(mask, (w, h))
    
    kernel = np.ones((12, 12), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_rgba[mask == 0, 3] = 0 

    coords = np.column_stack(np.where(mask > 0))
    if coords.size != 0:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        cropped_hand = img_rgba[y_min:y_max, x_min:x_max]
        return cv2.cvtColor(cropped_hand, cv2.COLOR_BGRA2RGBA)
    return None

if __name__ == "__main__":
    print("Run your GUI main.py to test integration.")