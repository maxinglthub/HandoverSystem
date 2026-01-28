import os
import datetime
from dataclasses import dataclass
from typing import List

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pygame

#import core.py
'''
try:
    from core import CoreClass
except:
    from core import CoreClass
'''


@dataclass
class Task:
    label: str
    when_checked: str
    when_unchecked: str = ""


class HandoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        print("hello")

        #icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        self.iconbitmap(icon_path)

        #mp3
        self.mp3_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mp3.mp3")

        #CTK主題
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("姑姑嘎嘎(2.0)")
        self.geometry("900x650")
        self.minsize(820, 560)

        #字體
        self.font_title = ctk.CTkFont(family="Consolas", size=18, weight="bold")
        self.font_main = ctk.CTkFont(family="Consolas", size=13)
        self.font_mono = ("Consolas", 13)

        #資料
        self.tasks: List[Task] = []
        self.vars: List[ctk.BooleanVar] = []

        #layout
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self.load_tasks()
        pygame.mixer.init()

    def _build_ui(self):
        #header
        print("build ui")
        header = ctk.CTkFrame(self, corner_radius=12)
        header.grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="牛馬交接系統", font=self.font_title).grid(
            row=0, column=0, padx=16, pady=12, sticky="w"
        )

        btn_play_mp3 = ctk.CTkButton(header, text="a", command=self.play_mp3)
        btn_play_mp3.grid(row=0, column=3, padx=18, sticky="w")

        #left tasks
        left = ctk.CTkFrame(self, corner_radius=12)
        left.grid(row=1, column=0, padx=(18, 9), pady=(0, 18), sticky="nsew")
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="待辦事項", font=self.font_main).grid(
            row=0, column=0, padx=16, pady=(14, 8), sticky="w"
        )

        self.task_scroll = ctk.CTkScrollableFrame(left, corner_radius=10)
        self.task_scroll.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.task_scroll.grid_columnconfigure(0, weight=1)

        #right textbox
        right = ctk.CTkFrame(self, corner_radius=12)
        right.grid(row=1, column=1, padx=(9, 18), pady=(0, 18), sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="輸出", font=self.font_main).grid(
            row=0, column=0, padx=16, pady=(14, 8), sticky="w"
        )

        self.textbox = ctk.CTkTextbox(right, font=self.font_mono, wrap="word")
        self.textbox.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")
        btn_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(btn_row, text="複製", command=self.copy_to_clipboard).grid(
            row=0, column=0, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(btn_row, text="重置", command=self.load_tasks).grid(
            row=0, column=1, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(btn_row, text="全選", command=self.select_all).grid(
            row=0, column=2, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(btn_row, text="全不選", command=self.clear_all).grid(
            row=0, column=3, sticky="ew"
        )

    def _tasks_file(self) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "tasks.txt")

    def load_tasks(self):
        print("load tasks(reset)")
        #重置
        for w in self.task_scroll.winfo_children():
            w.destroy()
        self.tasks.clear()
        self.vars.clear()

        path = self._tasks_file()

        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2:
                        label = parts[0]
                        t_true = parts[1]
                        t_false = parts[2] if len(parts) >= 3 else ""
                        self.tasks.append(Task(label, t_true, t_false))

            #checkbox
            for i, task in enumerate(self.tasks):
                var = ctk.BooleanVar(value=False)
                var.trace_add("write", lambda *_: self.generate_text())
                self.vars.append(var)

                cb = ctk.CTkCheckBox(
                    self.task_scroll,
                    text=task.label,
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    font=self.font_main,
                )
                cb.grid(row=i, column=0, sticky="w", padx=8, pady=6)

            self.generate_text()

        except Exception as e:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", f"讀取 tasks.txt 失敗：{e}")

    def generate_text(self):
        today = datetime.datetime.now().strftime("%Y/%m/%d")
        header = (
            f"{today} 工讀生交接:\n"
            "今日出、改單:\n\n"
            "今日設定WIFI機、無紙化設定:\n\n"
            "其他事項:\n"
        )

        lines: List[str] = []
        has_any = False

        for var, task in zip(self.vars, self.tasks):
            content = task.when_checked if var.get() else task.when_unchecked
            if content:
                lines.append(content)
                has_any = True

        tail = "\n工讀生交接&維修:"
        if not has_any:
            tail += "(無特殊回報事項)"

        output = header + ("\n".join(lines) + "\n" if lines else "") + tail

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", output)

    def copy_to_clipboard(self):
        print("copy to clipboard")
        content = self.textbox.get("1.0", "end").rstrip()
        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        messagebox.showinfo("系統提示", "內容已複製")

    def select_all(self):
        print("select all")
        for v in self.vars:
            v.set(True)

    def clear_all(self):
        print("clear all")
        for v in self.vars:
            v.set(False)

    #gugugaga
    def play_mp3(self):
        print("play mp3")
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.mp3_path)
        pygame.mixer.music.play()

if __name__ == "__main__":
    app = HandoverApp()
    app.mainloop()