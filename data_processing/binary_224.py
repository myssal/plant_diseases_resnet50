import os
from PIL import Image
from tqdm import tqdm

# 1. Đường dẫn nguồn (Thư mục bạn vừa tạo ở bước trước)
src_dir = r"/plant_leaves_new"

# 2. Đường dẫn đích (Thư mục mới cho bài toán Binary và đã được tối ưu cho ResNet50)
dst_dir = r"/plant_leaves_binary_224"

# Tạo 2 thư mục con là diseased và healthy
for status in ['diseased', 'healthy']:
    os.makedirs(os.path.join(dst_dir, status), exist_ok=True)

# Lấy danh sách các thư mục P0 -> P9
p_folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]

print(f"Bắt đầu gom và Resize ảnh về 224x224 cho ResNet-50...")
print(f"Đích đến: {dst_dir}\n")

# Đếm tổng số ảnh để hiển thị thanh tiến trình tổng quan
total_images = 0
for p_folder in p_folders:
    for status in ['diseased', 'healthy']:
        status_path = os.path.join(src_dir, p_folder, status)
        if os.path.exists(status_path):
            total_images += len(os.listdir(status_path))

# Sử dụng tqdm để theo dõi tiến trình xử lý
with tqdm(total=total_images, desc="Đang xử lý ảnh") as pbar:
    for p_folder in p_folders:
        p_path = os.path.join(src_dir, p_folder)

        for status in ['diseased', 'healthy']:
            src_status_path = os.path.join(p_path, status)
            dst_status_path = os.path.join(dst_dir, status)

            if not os.path.exists(src_status_path):
                continue

            for img_name in os.listdir(src_status_path):
                src_img_path = os.path.join(src_status_path, img_name)
                dst_img_path = os.path.join(dst_status_path, img_name)

                # Chỉ xử lý nếu file chưa tồn tại ở đích
                if not os.path.exists(dst_img_path):
                    try:
                        # Mở ảnh bằng Pillow
                        with Image.open(src_img_path) as img:
                            # Đảm bảo ảnh ở hệ màu RGB (tránh lỗi với ảnh RGBA/Grayscale)
                            if img.mode != 'RGB':
                                img = img.convert('RGB')

                            # Resize ảnh về 224x224 sử dụng thuật toán nội suy LANCZOS (cho chất lượng tốt nhất)
                            img_resized = img.resize((224, 224), Image.Resampling.LANCZOS)

                            # Lưu ảnh
                            img_resized.save(dst_img_path, quality=95)

                    except Exception as e:
                        print(f"\n[Lỗi] Không thể xử lý file {src_img_path}: {e}")

                pbar.update(1)

print("\nHoàn tất! Dữ liệu của bạn đã sẵn sàng 100% cho ResNet-50.")