import os
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data2", "India")
EXCEL_PATH = os.path.join(BASE_DIR, "data2", "India.xlsx")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

IMG_SIZE = 256
BATCH_SIZE = 8
EPOCHS = 80
LR = 5e-5