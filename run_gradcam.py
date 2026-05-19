# run_predict.py
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from tensorflow.keras.models import Model

# Import công cụ quản lý file của bạn
import file_manager as fm


# ==========================================
# 1. HÀM CHUẨN BỊ ẢNH
# ==========================================
def get_img_array(img_path, size=(224, 224)):
    """Đọc ảnh từ ổ cứng và biến đổi thành ma trận số để AI đọc được"""
    img = load_img(img_path, target_size=size)
    array = img_to_array(img)
    array = np.expand_dims(array, axis=0)  # Thêm chiều batch (1, 224, 224, 3)
    return array


# ==========================================
# 2. CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == "__main__":
    # Lấy đường dẫn từ file_manager
    model_path = fm.get_model_path("plant_leaves_resnet_with_augmentation.keras")
    test_img_path = fm.get_test_image("image_test_4.JPG")  # Đổi tên ảnh bạn muốn test vào đây

    # --- DỰNG KHUNG VÀ NẠP TRỌNG SỐ ---
    print("Đang khởi tạo hệ thống AI...")
    base_model = ResNet50(weights=None, include_top=False, input_shape=(224, 224, 3))

    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.2)(x)
    x = Dense(512, activation='relu')(x)
    output = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.load_weights(model_path)
    print("✅ Đã nạp mô hình thành công!\n")

    # --- ĐỌC ẢNH VÀ DỰ ĐOÁN ---
    print(f"Đang phân tích ảnh: {test_img_path}")
    img_array = get_img_array(test_img_path)

    # Lệnh predict trả về một mảng, ta lấy giá trị đầu tiên [0][0]
    pred = model.predict(img_array, verbose=0)[0][0]

    # --- IN KẾT QUẢ ---
    print("\n" + "=" * 50)
    if pred < 0.5:
        # Nếu theo quy ước lúc train: 0 là Bệnh, 1 là Khỏe
        do_tu_tin = (1 - pred) * 100
        print(f"⚠️ CẢNH BÁO: LÁ CÓ LỖI / BỊ BỆNH")
        print(f"Độ tự tin của AI: {do_tu_tin:.2f}%")

        # (Tùy chọn) Lưu lịch sử test
        fm.save_log(f"Phát hiện LỖI: {test_img_path} - Tự tin: {do_tu_tin:.2f}%")
    else:
        do_tu_tin = pred * 100
        print(f"✅ KẾT QUẢ: LÁ KHỎE MẠNH / BÌNH THƯỜNG")
        print(f"Độ tự tin của AI: {do_tu_tin:.2f}%")

        # (Tùy chọn) Lưu lịch sử test
        fm.save_log(f"Khỏe mạnh: {test_img_path} - Tự tin: {do_tu_tin:.2f}%")
    print("=" * 50)