import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import file_manager as fm
from app_config import COLORS, DEVICE
from custom_widgets import RoundedButton
from detector import PlantDetector

class PlantDiseaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô hình phát hiện sâu bệnh lá cây")
        
        # set full window
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1200x800")
            
        self.root.configure(bg=COLORS["bg"])

        self.detector = PlantDetector()
        self.image_list = [] 
        self.zoom_level = 1.0
        self.original_preview_img = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # header bar
        nav_frame = tk.Frame(self.root, bg="white", height=80, bd=0)
        nav_frame.pack(fill=tk.X, side=tk.TOP)
        nav_frame.pack_propagate(False)

        title_label = tk.Label(nav_frame, text="Mô hình phát hiện sâu bệnh lá cây", 
                              font=("Segoe UI", 20, "bold"), 
                              bg="white", fg=COLORS["secondary"])
        title_label.pack(side=tk.LEFT, padx=40)

        btn_container = tk.Frame(nav_frame, bg="white")
        btn_container.pack(side=tk.RIGHT, padx=40)

        self.btn_select_files = RoundedButton(btn_container, 140, 45, 22, 0, COLORS["primary"], "Thêm Ảnh", self.select_files, font=("Segoe UI", 11, "bold"))
        self.btn_select_files.pack(side=tk.LEFT, padx=5)

        self.btn_select_folder = RoundedButton(btn_container, 160, 45, 22, 0, COLORS["primary"], "Thêm Thư Mục", self.select_folder, font=("Segoe UI", 11, "bold"))
        self.btn_select_folder.pack(side=tk.LEFT, padx=5)
        
        self.btn_run = RoundedButton(btn_container, 160, 45, 22, 0, "#3498db", "Chạy Phân Tích", self.start_prediction, font=("Segoe UI", 11, "bold"))
        self.btn_run.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = RoundedButton(btn_container, 120, 45, 22, 0, COLORS["danger"], "Xóa Tất Cả", self.clear_all, font=("Segoe UI", 11, "bold"))
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # main area
        main_container = tk.Frame(self.root, bg=COLORS["bg"], padx=40, pady=30)
        main_container.pack(fill=tk.BOTH, expand=True)

        # fixed ratio headers
        table_header = tk.Frame(main_container, bg="white", height=60, bd=0, highlightthickness=1, highlightbackground="#dcdde1")
        table_header.pack(fill=tk.X)
        table_header.pack_propagate(False)

        header_data = [("Hình ảnh", 0.12), ("Tên file", 0.30), ("Chuẩn đoán chi tiết", 0.48), ("Độ tin cậy", 0.10)]
        for text, ratio in header_data:
            lbl_frame = tk.Frame(table_header, bg="white")
            lbl_frame.place(relx=sum(h[1] for h in header_data[:header_data.index((text, ratio))]), 
                           rely=0, relwidth=ratio, relheight=1)
            lbl = tk.Label(lbl_frame, text=text, font=("Segoe UI", 12, "bold"), bg="white", fg=COLORS["header"])
            lbl.pack(expand=True)

        # scrollable list
        list_container = tk.Frame(main_container, bg=COLORS["bg"])
        list_container.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.canvas = tk.Canvas(list_container, bg=COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Status Bar
        self.status_frame = tk.Frame(self.root, bg="white", height=35, bd=0)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(self.status_frame, text="Sẵn sàng", font=("Segoe UI", 9), bg="white", fg="#7f8c8d")
        self.status_label.pack(side=tk.LEFT, padx=30)

    def _on_mousewheel(self, event):
        if hasattr(self, 'overlay'): return
        if self.canvas.bbox("all")[3] > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def select_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.JPG *.PNG")])
        if paths:
            for path in paths: self.add_image_row(path)
            self.status_label.config(text=f"Đã thêm {len(paths)} ảnh mới")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG', '.PNG'))]
            for path in paths: self.add_image_row(path)
            self.status_label.config(text=f"Đã thêm {len(paths)} ảnh từ thư mục")

    def add_image_row(self, path):
        if any(item['path'] == path for item in self.image_list): return
        card = tk.Frame(self.scrollable_frame, bg="white", height=90, highlightthickness=1, highlightbackground="#f1f2f6")
        card.pack(fill=tk.X, pady=3)
        card.pack_propagate(False)
        
        ratios = [0.12, 0.30, 0.48, 0.10]
        curr_x = 0
        img_container = tk.Frame(card, bg="white")
        img_container.place(relx=curr_x, relwidth=ratios[0], relheight=1)
        try:
            img = Image.open(path)
            img.thumbnail((65, 65))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(img_container, image=photo, bg="white", cursor="hand2")
            img_label.image = photo 
            img_label.pack(expand=True)
            img_label.bind("<Button-1>", lambda e, p=path: self.show_large_image(p))
        except:
            tk.Label(img_container, text="Error", fg="red", bg="white").pack(expand=True)
        
        curr_x += ratios[0]
        name_container = tk.Frame(card, bg="white")
        name_container.place(relx=curr_x, relwidth=ratios[1], relheight=1)
        tk.Label(name_container, text=os.path.basename(path), bg="white", font=("Segoe UI", 10), fg=COLORS["text"], anchor="w").pack(side=tk.TOP, fill=tk.X, padx=15, pady=(25, 0))
        tk.Label(name_container, text=path[:40]+"...", bg="white", font=("Segoe UI", 8), fg="#bdc3c7", anchor="w").pack(side=tk.TOP, fill=tk.X, padx=15)
        
        curr_x += ratios[1]
        diag_container = tk.Frame(card, bg="white")
        diag_container.place(relx=curr_x, relwidth=ratios[2], relheight=1)
        diag_label = tk.Label(diag_container, text="Chờ xử lý", bg="white", font=("Segoe UI", 11, "bold"), fg="#95a5a6", wraplength=450, justify=tk.CENTER)
        diag_label.pack(expand=True, fill=tk.BOTH)
        
        curr_x += ratios[2]
        conf_container = tk.Frame(card, bg="white")
        conf_container.place(relx=curr_x, relwidth=ratios[3], relheight=1)
        conf_label = tk.Label(conf_container, text="--%", bg="white", font=("Segoe UI", 11), fg="#7f8c8d")
        conf_label.pack(expand=True)

        self.image_list.append({'path': path, 'diag_label': diag_label, 'conf_label': conf_label, 'frame': card})

    def clear_all(self):
        for item in self.image_list: item['frame'].destroy()
        self.image_list = []
        self.status_label.config(text="Đã xóa danh sách")

    def start_prediction(self):
        if not self.image_list:
            messagebox.showwarning("Thông báo", "Vui lòng chọn ảnh trước!")
            return
        
        # buttons disable
        for btn in [self.btn_run, self.btn_select_files, self.btn_select_folder, self.btn_clear]:
            btn.config_state(tk.DISABLED)
            
        threading.Thread(target=self.run_prediction_thread, daemon=True).start()

    def run_prediction_thread(self):
        # model loading feedback
        if self.detector.model is None:
            self.root.after(0, lambda: self.status_label.config(text="Đang nạp mô hình PyTorch..."))
            if not self.detector.load_model():
                self.root.after(0, self.finish_prediction)
                return

        for item in self.image_list:
            if item['diag_label'].cget("text") not in ["Chờ xử lý", "Lỗi"]: continue
            path = item['path']
            self.root.after(0, lambda p=path: self.status_label.config(text=f"🔍 Đang phân tích: {os.path.basename(p)}"))
            
            result = self.detector.predict(path)
            if result:
                predicted_class, confidence = result
                is_healthy = "healthy" in predicted_class.lower()
                fg = "#2ecc71" if is_healthy else "#e74c3c"
                display_name = predicted_class.replace("___", ": ").replace("_", " ")
                
                self.root.after(0, lambda i=item, r=display_name, c=confidence, f=fg: self.update_row(i, r, c, f))
                fm.save_log(f"{predicted_class}: {path} - Tự tin: {confidence:.2f}%")
            else:
                self.root.after(0, lambda i=item: i['diag_label'].config(text="Lỗi", fg="#e67e22"))

        self.root.after(0, self.finish_prediction)

    def update_row(self, item, res_text, conf, fg_color):
        item['diag_label'].config(text=res_text, fg=fg_color, bg="white")
        item['conf_label'].config(text=f"{conf:.2f}%", fg=fg_color)

    def finish_prediction(self):
        self.status_label.config(text="Hoàn thành!")
        for btn in [self.btn_run, self.btn_select_files, self.btn_select_folder, self.btn_clear]:
            btn.config_state(tk.NORMAL)

    def show_large_image(self, path):
        self.overlay = tk.Frame(self.root, bg=COLORS["overlay"]) 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            self.original_preview_img = Image.open(path)
            self.zoom_level = 1.0
            self.img_view = tk.Label(self.overlay, bg=COLORS["overlay"])
            self.img_view.pack(expand=True)
            self._update_preview_image()
            
            self.overlay.bind("<Button-1>", lambda e: self.close_large_image())
            self.img_view.bind("<Button-1>", lambda e: self.close_large_image())
            self.root.bind_all("<MouseWheel>", self._on_preview_zoom)
        except:
            self.close_large_image()

    def _update_preview_image(self):
        if not self.original_preview_img: return
        win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
        base_w, base_h = self.original_preview_img.size
        scale = min((win_w - 100) / base_w, (win_h - 100) / base_h)
        new_size = (int(base_w * scale * self.zoom_level), int(base_h * scale * self.zoom_level))
        if new_size[0] < 10 or new_size[1] < 10: return
        resized_img = self.original_preview_img.resize(new_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_img)
        self.img_view.config(image=photo)
        self.img_view.image = photo

    def _on_preview_zoom(self, event):
        if hasattr(self, 'overlay'):
            if event.delta > 0: self.zoom_level *= 1.1
            else: self.zoom_level /= 1.1
            self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
            self._update_preview_image()
        else: self._on_mousewheel(event)

    def close_large_image(self):
        if hasattr(self, 'overlay'):
            self.root.unbind_all("<MouseWheel>")
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self.overlay.destroy()
            del self.overlay
            self.original_preview_img = None

if __name__ == "__main__":
    root = tk.Tk()
    app = PlantDiseaseApp(root)
    root.mainloop()
