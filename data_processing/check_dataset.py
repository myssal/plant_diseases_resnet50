import os
from PIL import Image
from tqdm import tqdm


def check_dataset_health(root_dir):
    print("\n" + "=" * 80)
    print(f"ĐANG KIỂM TRA THƯ MỤC: {root_dir}")
    print(f"{'Folder Path':<60} | {'Total':<8} | {'Corrupt':<8}")
    print("-" * 80)

    total_images = 0
    total_corrupt = 0

    for root, dirs, files in os.walk(root_dir):
        if not files:
            continue
        folder_count = 0
        corrupt_count = 0
        corrupt_files = []

        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                folder_count += 1
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                except (IOError, SyntaxError) as e:
                    corrupt_count += 1
                    corrupt_files.append(file_path)

        if folder_count > 0:
            relative_path = os.path.relpath(root, root_dir)
            print(f"{relative_path:<60} | {folder_count:<8} | {corrupt_count:<8}")
            if corrupt_files:
                print("   --> File lỗi:")
                for cf in corrupt_files:
                    print(f"       [!] {cf}")

        total_images += folder_count
        total_corrupt += corrupt_count

    print("-" * 80)
    print(f"TỔNG CỘNG: {total_images} ảnh | Phát hiện {total_corrupt} file lỗi.")
    print("=" * 80)


def check_dataset_plant_leaves_binary_224(root_dir):
    print("\n" + "=" * 80)
    print(f"ĐANG KIỂM TRA THƯ MỤC BINARY: {root_dir}")

    corrupted_files = []
    all_files = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                all_files.append(os.path.join(root, file))

    print(f"Đang kiểm tra tổng cộng {len(all_files)} ảnh...")

    for file_path in tqdm(all_files, desc="Tiến trình kiểm tra"):
        try:
            # Mở và verify() chỉ kiểm tra header của ảnh, rất nhanh và nhẹ
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            corrupted_files.append(file_path)

    print("-" * 80)
    if not corrupted_files:
        print("✅ XUẤT SẮC! Không phát hiện ảnh nào bị lỗi. Dữ liệu đã sẵn sàng 100%.")
    else:
        print(f"❌ CẢNH BÁO: Phát hiện {len(corrupted_files)} ảnh bị hỏng/lỗi:")
        for path in corrupted_files:
            print(f"  --> {path}")
    print("=" * 80)


def run():
    while True:
        print("\n" + "*" * 40)
        print("   CÔNG CỤ KIỂM TRA LỖI DỮ LIỆU ẢNH   ")
        print("*" * 40)
        print("1. Kiểm tra Folder: plant_leaves (Bộ gốc)")
        print("2. Kiểm tra Folder: plant_leaves_new (Đã phân loại Px)")
        print("3. Kiểm tra Folder: plant_leaves_binary_224 (Đã Resize)")
        print("4. Thoát chương trình!")
        print("*" * 40)

        try:
            x = int(input("Nhập lựa chọn của bạn (1-4): "))
        except ValueError:
            print("\n[Lỗi] Vui lòng chỉ nhập một số nguyên!")
            continue

        if x == 1:
            check_dataset_health(r"/plant_leaves")
        elif x == 2:
            check_dataset_health(r"/plant_leaves_new")
        elif x == 3:
            check_dataset_plant_leaves_binary_224(r"/plant_leaves_binary_224")
        elif x == 4:
            print("\nĐã thoát chương trình. Chúc bạn huấn luyện mô hình thành công!")
            break
        else:
            print("\n[Lỗi] Lựa chọn không hợp lệ. Vui lòng nhập số từ 1 đến 4.")


# Gọi hàm để chạy giao diện
if __name__ == "__main__":
    run()