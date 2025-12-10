import tkinter as tk
from tkinter import messagebox
import datetime
import os

class HandoverSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("工讀生交接系統")
        self.root.geometry("800x600")
        
        # --- 色票與風格設定 (您可以根據您的客戶管理系統調整這裡) ---
        self.colors = {
            "bg_main": "#2D2D30",       # 主視窗背景 (深灰)
            "bg_panel": "#3E3E42",      # 區塊背景 (略淺的灰)
            "fg_text": "#FFFFFF",       # 主要文字 (白)
            "fg_sub": "#CCCCCC",        # 次要文字 (淺灰)
            "accent": "#007ACC",        # 強調色 (藍色)
            "btn_bg": "#007ACC",        # 按鈕背景
            "btn_fg": "#FFFFFF",        # 按鈕文字
            "input_bg": "#1E1E1E",      # 輸入框背景 (更深)
            "input_fg": "#FFFFFF"       # 輸入框文字
        }
        
        self.font_title = ("Microsoft JhengHei", 14, "bold")
        self.font_main = ("Microsoft JhengHei", 11)
        
        # 套用主背景色
        self.root.configure(bg=self.colors["bg_main"])
        
        # 資料變數
        self.tasks = []
        self.check_vars = []
        
        # 初始化介面
        self.setup_ui()
        
        # 讀取設定
        self.load_config()

    def setup_ui(self):
        """建立現代化深色介面"""
        
        # --- 標題列 ---
        header_frame = tk.Frame(self.root, bg=self.colors["bg_main"], pady=10)
        header_frame.pack(fill=tk.X, padx=20)
        
        lbl_title = tk.Label(header_frame, text="每日交接事項清單", 
                             font=self.font_title, 
                             bg=self.colors["bg_main"], fg=self.colors["fg_text"])
        lbl_title.pack(side=tk.LEFT)

        # --- 主內容區 (分為左右兩邊) ---
        main_content = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # === 左側：選項區 ===
        self.left_panel = tk.Frame(main_content, bg=self.colors["bg_panel"], padx=2, pady=2)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 左側標題
        tk.Label(self.left_panel, text="  待辦事項 (勾選代表已完成)", 
                 font=self.font_main, bg=self.colors["bg_panel"], fg=self.colors["accent"], anchor="w", pady=10).pack(fill=tk.X)

        # 捲動區塊 (為了美觀，這裡做一點層次)
        canvas_frame = tk.Frame(self.left_panel, bg=self.colors["bg_panel"])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(canvas_frame, bg=self.colors["bg_panel"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview, bg=self.colors["bg_panel"])
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg_panel"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        # === 右側：預覽區 ===
        self.right_panel = tk.Frame(main_content, bg=self.colors["bg_panel"])
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # 右側標題
        tk.Label(self.right_panel, text="  交接內容預覽", 
                 font=self.font_main, bg=self.colors["bg_panel"], fg=self.colors["accent"], anchor="w", pady=10).pack(fill=tk.X)

        # 文字輸出框 (深底白字)
        self.result_text = tk.Text(self.right_panel, height=15, width=30, 
                                   font=("Consolas", 11), # 用等寬字體看起來像程式碼或系統log
                                   bg=self.colors["input_bg"], 
                                   fg=self.colors["input_fg"],
                                   insertbackground="white", # 游標顏色
                                   relief="flat", padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # 按鈕區
        btn_frame = tk.Frame(self.right_panel, bg=self.colors["bg_panel"])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.create_styled_button(btn_frame, " 複製內容 ", self.copy_to_clipboard).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.create_styled_button(btn_frame, " 重新讀取設定 ", self.load_config).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def create_styled_button(self, parent, text, command):
        """建立統一風格的按鈕"""
        btn = tk.Button(parent, text=text, command=command,
                        bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
                        font=self.font_main, relief="flat",
                        activebackground=self.colors["fg_text"], 
                        activeforeground=self.colors["bg_main"],
                        cursor="hand2", pady=5)
        return btn

    def load_config(self):
        file_path = "tasks.txt"
        
        # 清空舊元件
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.tasks.clear()
        self.check_vars.clear()

        if not os.path.exists(file_path):
            self.create_dummy_file(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"): continue
                
                parts = line.split("|")
                if len(parts) >= 2:
                    label_name = parts[0].strip()
                    text_true = parts[1].strip()
                    text_false = parts[2].strip() if len(parts) > 2 else ""
                    self.tasks.append((label_name, text_true, text_false))
            
            self.create_checkboxes()
            self.generate_text()
            
        except Exception as e:
            self.result_text.insert(tk.END, f"錯誤: {str(e)}")

    def create_dummy_file(self, path):
        content = """開店清潔|店面已完成清潔消毒|店面尚未清潔
檢查零錢|零錢備用金充足|零錢不足，需換錢
補飲料|冰箱飲料已補滿|部分飲料缺貨
倒垃圾|垃圾已清運|垃圾未清運"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def create_checkboxes(self):
        """在深色背景上建立勾選框"""
        for i, (label_name, _, _) in enumerate(self.tasks):
            var = tk.BooleanVar(value=False)
            
            # Checkbutton 在深色模式下的設定比較繁瑣
            chk = tk.Checkbutton(
                self.scrollable_frame, 
                text=label_name, 
                variable=var, 
                command=self.generate_text,
                bg=self.colors["bg_panel"],
                fg=self.colors["fg_text"],
                selectcolor=self.colors["input_bg"], # 勾選框內部的顏色
                activebackground=self.colors["bg_panel"],
                activeforeground=self.colors["accent"],
                font=self.font_main,
                pady=5
            )
            chk.pack(anchor="w", fill=tk.X)
            self.check_vars.append(var)

    def generate_text(self):
        today = datetime.datetime.now().strftime("%Y/%m/%d")
        output = f"{today} 工讀生交接: \n"
        
        has_content = False
        
        for i, var in enumerate(self.check_vars):
            is_checked = var.get()
            _, text_true, text_false = self.tasks[i]
            
            content = text_true if is_checked else text_false
            
            if content:
                # 使用簡單的符號列表
                mark = "[v]" if is_checked else "[ ]"
                output += f"{mark} {content}\n"
                has_content = True
        
        if not has_content:
            output += "(無特殊回報事項)"

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", output)

    def copy_to_clipboard(self):
        content = self.result_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("系統提示", "內容已複製")

if __name__ == "__main__":
    root = tk.Tk()
    app = HandoverSystem(root)
    root.mainloop()