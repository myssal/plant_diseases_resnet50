from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

def get_model_path(model_name = "plant_leaves_resnet.keras"):
    path = BASE_DIR / "models" / model_name
    if not path.exists(): raise FileNotFoundError(f"Không tìm thấy file model")
    return str(path)

def get_test_image(image_name):
    path = BASE_DIR / "test_image" / image_name
    if not path.exists(): raise FileNotFoundError(f"Không tìm thấy ảnh tại: {path}")
    return str(path)

def save_log(content, filename = "results.txt"):
    log_path = BASE_DIR / filename
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")