import os
import shutil
import re
from tqdm import tqdm

# 1. Khai báo thư mục gốc và thư mục mới
src_dir = r"/plant_leaves"
dst_dir = r"/plant_leaves_new"

# 2. Quy tắc ánh xạ (Mapping) dịch chuyển các P
# old_p : new_p (Bỏ qua 4 và 8)
p_mapping = {
    0: 0, 1: 1, 2: 2, 3: 3,
    # Bỏ P4
    5: 4, 6: 5, 7: 6,
    # Bỏ P8
    9: 7, 10: 8, 11: 9
}

# Tạo thư mục mới nếu chưa có
os.makedirs(dst_dir, exist_ok=True)

# Lấy danh sách các thư mục cây trong thư mục gốc
tree_folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]

print(f"Bắt đầu xử lý dữ liệu từ: {src_dir}")
print(f"Đích đến: {dst_dir}\n")

for folder_name in tqdm(tree_folders, desc="Đang xử lý các thư mục"):
    # Trích xuất số P cũ từ tên thư mục (vd: "Mango (P0)" -> 0)
    match = re.search(r'\(P(\d+)\)', folder_name)
    if not match:
        continue

    old_p_id = int(match.group(1))

    # Nếu mã P cũ không có trong danh sách mapping (tức là P4 hoặc P8) -> Bỏ qua
    if old_p_id not in p_mapping:
        continue

    # Lấy mã P mới
    new_p_id = p_mapping[old_p_id]
    new_p_folder = f"P{new_p_id}"

    # Tạo đường dẫn thư mục P mới
    dst_tree_path = os.path.join(dst_dir, new_p_folder)

    # Duyệt qua 2 thư mục con: diseased (0) và healthy (1)
    for status in ['diseased', 'healthy']:
        src_status_path = os.path.join(src_dir, folder_name, status)
        dst_status_path = os.path.join(dst_tree_path, status)

        # Mã hóa trạng thái: healthy = 1, diseased = 0
        status_code = 1 if status == 'healthy' else 0

        if os.path.exists(src_status_path):
            # Tạo thư mục diseased/healthy bên trong thư mục Px mới
            os.makedirs(dst_status_path, exist_ok=True)

            # Lấy danh sách file và sắp xếp để đánh số thứ tự chuẩn xác
            files = sorted(os.listdir(src_status_path))

            # Khởi tạo bộ đếm thứ tự ảnh (bắt đầu từ 1)
            seq_num = 1

            for filename in files:
                # Lấy phần mở rộng của file (vd: .jpg, .JPG, .png)
                ext = os.path.splitext(filename)[1]

                # Format tên mới: {new_p_id}_{status_code}_{seq_num}.jpg
                # seq_num:04d đảm bảo số có 4 chữ số (0001, 0002)
                new_filename = f"{new_p_id}_{status_code}_{seq_num:04d}{ext}"

                src_file_path = os.path.join(src_status_path, filename)
                dst_file_path = os.path.join(dst_status_path, new_filename)

                # Copy file sang thư mục mới với tên mới
                if not os.path.exists(dst_file_path):
                    shutil.copy2(src_file_path, dst_file_path)

                seq_num += 1

print("\nHoàn tất quá trình tiền xử lý!")
print(f"Bạn có thể kiểm tra dữ liệu tại: {dst_dir}")