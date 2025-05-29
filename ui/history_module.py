import os
import datetime
import json
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from ui.result_module import create_result_content

HISTORY_PATH = os.path.join("data", "history")
DATE_FORMAT = "%Y%m%d_%H%M%S"


@dataclass
class HistoryData:

    path: str
    date: datetime.datetime
    raw: dict


class HistoryView:
    """
    顯示歷史紀錄清單 (Treeview)。可以從清單內點選，即可在結果畫面顯示當時的分析結果。

    Arguments:
        parent (tk.Frame): 此 Treeview 要放在哪個 Frame 內
        right_frame (tk.Frame): 此 TreeView 要連動哪一個 Frame 更新
    """

    def __init__(self, parent: tk.Frame, right_frame: tk.Frame) -> None:
        self.right_frame = right_frame

        frame = tk.Frame(parent)
        self.frame = frame

        # Title
        title = tk.Label(frame, text="歷史紀錄", font=("Arial", 11, "bold"))
        title.pack(anchor="w")

        # Make Treeview
        columns = ["時間", "輸入"]
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("時間", width=0)

        # 讓此 Treeview 連動一個 Scrollbar
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)
        self.tree.pack(fill="both", expand=True)

        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="刪除", command=self.delete_selected)

        # 左鍵點擊後更新右側結果
        self.tree.bind('<Button-1>', self.on_single_click)
        # 右鍵點擊後顯示選單
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 載入歷史資料
        self.history: list[HistoryData] = []
        self.update_history_data()

    def get_index(self, item: str):
        """回覆該 item 是第幾筆資料"""
        all_items = self.tree.get_children()
        index = all_items.index(item)
        return index

    def display_result(self, result_data: dict | None):
        """
        更新右側結果

        Parameters:
            result_data (dict | None): 用來更新右側結果的資料
        """
        # 清空現有內容
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        result_frame1 = create_result_content(self.right_frame, result_data)
        result_frame1.pack(expand=True, fill="both", padx=10, pady=10)

    def on_single_click(self, event: tk.Event):
        """單擊事件"""
        # 取得滑鼠所在位置對應的 item
        item = self.tree.identify_row(event.y)
        if item:
            index = self.get_index(item)
            self.display_result(result_data=self.history[index].raw)

    def show_context_menu(self, event: tk.Event):
        """顯示右鍵選單"""
        # 取得滑鼠所在位置對應的 item
        item = self.tree.identify_row(event.y)
        if item:
            selected_items = self.tree.selection()
            # item 不是原本 tree 中被選到的，則強制選擇這項
            if item not in selected_items:
                self.tree.selection_set(item)
                self.tree.focus(item)

                self.on_single_click(event)

            # 顯示選單
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    # def hide_context_menu(self, event: tk.Event):
    #     """隱藏右鍵選單"""
    #     self.context_menu.unpost()

    def delete_selected(self):
        """刪除所有選擇的項目"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        for item in selected_items:
            index = self.get_index(item)
            full_path = self.history[index].path
            os.remove(full_path)

        self.update_history_data()
        self.display_result(None)

    def update_history_data(self) -> None:
        """重新載入歷史資料"""
        history: list[HistoryData] = []

        # 讀取指定資料夾下的所有檔案
        files = os.listdir(HISTORY_PATH)
        files.sort(reverse=True)
        for file_name in files:
            full_path = os.path.join(HISTORY_PATH, file_name)

            # 忽略特定檔案名稱及格式
            if file_name.startswith("saved_settings"):
                continue
            if not file_name.endswith(".json"):
                continue
            if not os.path.isfile(full_path):
                continue

            # 分離檔案名稱及副檔名
            name, ext = os.path.splitext(file_name)
            try:
                date = datetime.datetime.strptime(name, DATE_FORMAT)
                with open(full_path, encoding="utf-8") as file:
                    raw = json.load(file)

                # 新增資料
                history_data = HistoryData(full_path, date, raw)
                history.append(history_data)
            except Exception as e:
                print(e, "This file can't not be read!")
                pass

        self.history = history

        # 刪除 treeview 中舊有的資料
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 以 history 更新 treeview
        for history_data in history:
            date = history_data.date
            raw = history_data.raw
            date_string = date.strftime("%Y/%m/%d %H:%M:%S")
            input_type = raw.get("input_type")
            input_value = raw.get("input_value", "")
            contents = f"{input_type} {input_value}"
            self.tree.insert("", "end", values=(date_string, contents))
