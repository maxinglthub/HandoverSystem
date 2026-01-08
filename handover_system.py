import tkinter
from tkinter import messagebox
import customtkinter as ctk
import datetime
import os
from typing import List, Dict, Optional


#出單設定檔案
LIST: Dict[str, List[str]] = {
    "客戶編號": ["no"],
    "名字": ["name"],
    "ID": ["id"],
    "手機": ["phone"],
    "地址": ["adress"],
    "社區": ["apt"],
}

class HandoverSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("工讀生交接系統")
        self.root.geometry("800x600")
        
        self.colors = {
            "bg_main": "#2D2D30",       # 主視窗背景
            "bg_panel": "#3E3E42",      # 區塊背景
            "fg_text": "#FFFFFF",       # 主要文字
            "fg_sub": "#CCCCCC",        # 次要文字
            "accent": "#007ACC",        # 強調色
            "btn_bg": "#007ACC",        # 按鈕背景
            "btn_fg": "#FFFFFF",        # 按鈕文字
            "input_bg": "#1E1E1E",      # 輸入框背景
            "input_fg": "#FFFFFF"       # 輸入框文字
        }
        
        self.font_title = ("Microsoft JhengHei", 14, "bold")
        self.font_main = ("Microsoft JhengHei", 11)
        
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
        header_frame = tkinter.Frame(self.root, bg=self.colors["bg_main"], pady=10)
        header_frame.pack(fill=tkinter.X, padx=20)
        
        lbl_title = tkinter.Label(header_frame, text="每日交接事項清單", 
                             font=self.font_title, 
                             bg=self.colors["bg_main"], fg=self.colors["fg_text"])
        lbl_title.pack(side=tkinter.LEFT)

        # --- 主內容區 (分為左右兩邊) ---
        main_content = tkinter.Frame(self.root, bg=self.colors["bg_main"])
        main_content.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=10)

        # === 左側：選項區 ===
        self.left_panel = tkinter.Frame(main_content, bg=self.colors["bg_panel"], padx=2, pady=2)
        self.left_panel.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 10))
        self.display_tasks: List[str] = []
        
        # 左側標題
        tkinter.Label(self.left_panel, text="待辦事項", 
                 font=self.font_main, bg=self.colors["bg_panel"], fg=self.colors["accent"], anchor="w", pady=10).pack(fill=tkinter.X)

        # 捲動區塊
        canvas_frame = tkinter.Frame(self.left_panel, bg=self.colors["bg_panel"])
        canvas_frame.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=(0, 10))

        self.canvas = tkinter.Canvas(canvas_frame, bg=self.colors["bg_panel"], highlightthickness=0)
        self.scrollbar = tkinter.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview, bg=self.colors["bg_panel"])
        
        self.scrollable_frame = tkinter.Frame(self.canvas, bg=self.colors["bg_panel"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)


        # === 右側：預覽區 ===
        self.right_panel = tkinter.Frame(main_content, bg=self.colors["bg_panel"])
        self.right_panel.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=True, padx=(10, 0))

        # 右側標題
        tkinter.Label(self.right_panel, text="  交接內容預覽", 
                 font=self.font_main, bg=self.colors["bg_panel"], fg=self.colors["accent"], anchor="w", pady=10).pack(fill=tkinter.X)

        # 文字輸出框 (深底白字)
        self.result_text = tkinter.Text(self.right_panel, height=15, width=30, 
                                   font=("Consolas", 11),
                                   bg=self.colors["input_bg"], 
                                   fg=self.colors["input_fg"],
                                   insertbackground="white",
                                   relief="flat", padx=10, pady=10)
        self.result_text.pack(fill=tkinter.BOTH, expand=True, padx=15, pady=(0, 15))

        # 按鈕區
        btn_frame = tkinter.Frame(self.right_panel, bg=self.colors["bg_panel"])
        btn_frame.pack(fill=tkinter.X, padx=15, pady=(0, 15))

        self.create_styled_button(btn_frame, " 複製內容 ", self.copy_to_clipboard).pack(side=tkinter.LEFT, fill=tkinter.X, expand=True, padx=(0, 5))
        self.create_styled_button(btn_frame, " 重新讀取設定 ", self.load_config).pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True, padx=(5, 0))

    def create_styled_button(self, parent, text, command):
        """建立統一風格的按鈕"""
        btn = tkinter.Button(parent, text=text, command=command,
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
            self.result_text.insert(tkinter.END, f"錯誤: {str(e)}")

    def create_checkboxes(self):
        """在深色背景上建立勾選框"""
        for i, (label_name, _, _) in enumerate(self.tasks):
            var = tkinter.BooleanVar(value=False)
            
            chk = tkinter.Checkbutton(
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
            chk.pack(anchor="w", fill=tkinter.X)
            self.check_vars.append(var)

    def generate_text(self):
        today = datetime.datetime.now().strftime("%Y/%m/%d")
        output = f"{today} 工讀生交接: \n今日出、改單: \n\n今日設定WIFI機、無紙化設定: \n\n其他事項: \n"
        
        has_content = False
        
        for i, var in enumerate(self.check_vars):
            is_checked = var.get()
            _, text_true, text_false = self.tasks[i]
            
            content = text_true if is_checked else text_false
            
            if content:
                output += f"{content}\n"
                has_content = True
        
        output += f"\n工讀生交接&維修:"

        if not has_content:
            output += "(無特殊回報事項)"

        self.result_text.delete("1.0", tkinter.END)
        self.result_text.insert("1.0", output)

    def copy_to_clipboard(self):
        content = self.result_text.get("1.0", tkinter.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("系統提示", "內容已複製")

class new_ui(ctk.CTk):
    def __init__(self, root):
        self.root = root
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        self.title("姑姑嘎嘎(New_Ui_Ver)")
        self.geometry(f"{800}x{800}")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=3)

        #左側
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="牛馬交接系統", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.copy_button = ctk.CTkButton(self.sidebar_frame, text = "複製", command=self.copy_to_clipboard, font=ctk.CTkFont(size=15))
        self.copy_button.grid(row=5, column=0, padx=20, pady=20)

        #右側
        self.textbox = ctk.CTkTextbox(self, width=300, height=300,
                                      font=("Consolas", 16),
                                      padx=10, pady=10
                                      )
        self.textbox.grid(row=0, column=1, rowspan=4, padx=30, pady=20, sticky="nsew")

        

    def copy_to_clipboard(self):
        content = self.textbox.get("1.0", ctk.END)
        self.textbox.clipboard_clear()
        self.textbox.clipboard_append(content)
        messagebox.showinfo("Warning", "內容已複製")

        

        
    
        

if __name__ == "__main__":
    app = new_ui(ctk.CTk)
    app.mainloop()