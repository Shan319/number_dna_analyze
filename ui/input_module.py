# ui/input_module.py
import os
import json
from typing import Callable

import tkinter as tk
from tkinter import messagebox

from data.input_data import InputData, InputType
from ui.settings_module import SettingView
from controller.analysis_controller import analyze
from utils.validators import validate_all


class InputView:

    def __init__(self, parent: tk.Widget) -> None:
        """輸入畫面模組。

        Parameters
        ----------
        parent : tk.Widget
            輸入畫面要放置的父畫面
        right_frame : tk.Widget
            右側結果畫面
        history_update_cb : Callable
            歷史畫面的更新 callback
        """

        self.notify_update_history_view: Callable | None = None
        self.notify_update_result_view: Callable | None = None

        frame = tk.LabelFrame(parent, text="輸入區", font=("Arial", 14))
        self.frame = frame

        # ===== 基本輸入欄位 =====
        self.input_type_var = tk.StringVar()

        self.name_var = tk.StringVar()
        self.id_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.birth_var = tk.StringVar()
        self.custom_var = tk.StringVar()  # 英數混合

        self.settings_path = os.path.join("data", "history", "saved_settings.json")

        # ===== 放置輸入模組 =====
        radio_button_info = [("中文姓名（限中文）", InputType.NAME.value, self.name_var),
                             ("身分證字號", InputType.ID.value, self.id_var),
                             ("手機號碼（09xxxxxxxx）", InputType.PHONE.value, self.phone_var),
                             ("生日（yyyy/mm/dd）", InputType.BIRTH.value, self.birth_var),
                             ("自定義（可英數混合）", InputType.CUSTOM.value, self.custom_var)]
        row = 0
        for text, radio_variable, entry_value in radio_button_info:
            tk.Radiobutton(frame, text=text, variable=self.input_type_var,
                           value=radio_variable).grid(row=row, column=0, sticky="w")
            tk.Entry(frame, textvariable=entry_value, width=20).grid(row=row,
                                                                     column=1,
                                                                     columnspan=3,
                                                                     sticky="w")
            row += 1

        # ===== 插入設定條件模組 =====
        row += 1
        self.settings_frame = SettingView(frame)
        self.settings_frame.frame.grid(row=row, column=0, columnspan=4, pady=10)

        # 開啟時自動載入設定
        self.load_saved_settings()

        # ===== 按鈕列 =====
        row += 1
        tk.Button(frame, text="開始分析", command=self.on_analyze_click).grid(row=row, column=0, pady=5)
        tk.Button(frame, text="重置設定", command=self.on_reset_settings_click).grid(row=row,
                                                                                 column=1,
                                                                                 pady=5)
        tk.Button(frame, text="載入設定", command=self.on_load_settings_click).grid(row=row,
                                                                                column=2,
                                                                                pady=5)
        tk.Button(frame, text="儲存設定", command=self.on_save_settings).grid(row=row, column=3, pady=5)

    def load_input_data(self, input_data: InputData):
        """依照 input_data 載入畫面上的值。

        Parameters
        ----------
        input_data : InputData
            設定資料
        """
        input_type = input_data.input_type
        input_values = input_data.input_values

        self.input_type_var.set(input_type.value)
        self.name_var.set(input_values[InputType.NAME.value])
        self.id_var.set(input_values[InputType.ID.value])
        self.phone_var.set(input_values[InputType.PHONE.value])
        self.birth_var.set(input_values[InputType.BIRTH.value])
        self.custom_var.set(input_values[InputType.CUSTOM.value])

        self.settings_frame.load_settings(input_data)

    def load_saved_settings(self):
        """載入上次存的設定，若不存在檔案就取預設值。"""
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # 載入設定
            input_data = InputData(**settings)
            self.load_input_data(input_data)

        except FileNotFoundError:
            # 如果檔案不存在就讀預設值
            input_data = InputData()
            self.load_input_data(input_data)

    def dump_input_data(self) -> InputData:
        """將畫面上的設定值倒出成 InputData

        Returns
        -------
        InputData
            依照畫面上的設定值變成的 InputData
        """
        # 收集輸入資料 (傳入所有設定變量)
        input_data = self.settings_frame.dump_settings()

        # 讀取輸入及輸入類型
        input_type = InputType(self.input_type_var.get())
        input_values = {
            InputType.NAME.value: self.name_var.get().strip(),
            InputType.ID.value: self.id_var.get().strip(),
            InputType.PHONE.value: self.phone_var.get().strip(),
            InputType.BIRTH.value: self.birth_var.get().strip(),
            InputType.CUSTOM.value: self.custom_var.get().strip(),
        }

        input_data.input_type = input_type
        input_data.input_values = input_values
        return input_data

    def on_analyze_click(self):
        """點擊【分析】按鈕"""

        input_data = self.dump_input_data()

        # 檢查輸入是否合法
        errors = validate_all(input_data)
        if errors:
            messagebox.showerror("輸入錯誤", "\n".join(errors))
            return  # 停止執行，避免分析錯誤資料

        # 分析輸入資料
        result_data = analyze(input_data)
        if result_data.errors:
            messagebox.showerror("輸入錯誤", "\n".join(errors))
            return  # 停止執行，避免分析錯誤資料

        # 使用結果控制器處理結果 (保存並顯示結果)
        from controller.result_controller import ResultController
        result_controller = ResultController()

        # 處理結果 - 這會自動保存分析結果和輸入歷史
        result_controller.process_result(result_data=result_data, input_data=input_data)

        # 通知更新結果畫面
        if self.notify_update_result_view:
            self.notify_update_result_view(result_data)

        # 通知更新歷史畫面
        if self.notify_update_history_view:
            self.notify_update_history_view()

        # 提示用戶分析完成
        messagebox.showinfo("分析完成", "分析已完成，結果已保存到歷史記錄!")

    def on_reset_settings_click(self):
        """點擊【重置設定】按鈕"""
        input_data = InputData()
        self.load_input_data(input_data)

    def on_load_settings_click(self):
        """點擊【載入設定】按鈕"""
        self.load_saved_settings()

    def on_save_settings(self):
        """點擊【儲存設定】按鈕"""
        input_data = self.dump_input_data()

        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(input_data.model_dump(), f, ensure_ascii=False, indent=2)

        messagebox.showinfo("提示", f"設定已儲存到 {self.settings_path}！")
