import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

import file_manager as fm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Gọi lại cấu trúc ResNet-50 gốc
model = models.resnet50(weights=None)

num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 38)

# ==========================================
# BƯỚC 2: NẠP TRỌNG SỐ TỪ TỆP .PTH
# ==========================================
model_path = fm.get_model_path('best_resnet_plant.pth')

# Load weights vào model
model.load_state_dict(torch.load(model_path, map_location=device))
model = model.to(device)

#Đặt mô hình ở chế độ đánh giá (evaluation mode)
# Tắt Dropout và đóng băng Batch Normalization
model.eval()
print("✅ Đã nạp mô hình thành công và sẵn sàng dự đoán!")

# ==========================================
# BƯỚC 3: TIỀN XỬ LÝ ẢNH & DỰ ĐOÁN
# ==========================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# Hàm dự đoán
def predict_image(image_path, model, class_names):
    # 1. Đọc ảnh
    image = Image.open(image_path).convert('RGB')

    # 2. Tiền xử lý
    input_tensor = transform(image)

    # 3. PyTorch yêu cầu đầu vào là một batch (lô).
    input_batch = input_tensor.unsqueeze(0).to(device)

    # 4. Chạy mô hình
    with torch.no_grad():  # Tắt tính toán gradient
        output = model(input_batch)

    # 5. Lấy kết quả có xác suất cao nhất
    # Áp dụng softmax để lấy phần trăm (từ 0.0 đến 1.0)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    max_prob, predicted_idx = torch.max(probabilities, 0)

    predicted_class = class_names[predicted_idx.item()]
    confidence = max_prob.item() * 100

    print(f"Bệnh dự đoán: {predicted_class}")
    print(f"Độ tự tin: {confidence:.2f}%")


# ==========================================
# CHẠY THỬ NGHIỆM
# ==========================================
my_class_names = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___healthy',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___healthy',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___healthy',
    'Potato___Late_blight',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___healthy',
    'Strawberry___Leaf_scorch',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___healthy',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
]

test_image_path = fm.get_test_image("PotatoEarlyBlight5.JPG")

predict_image(test_image_path, model, my_class_names)