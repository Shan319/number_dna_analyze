# ui/input_module.py

import tkinter as tk
from tkinter import messagebox
import json
from ui.settings_module import create_settings_frame
from controller.analysis_controller import analyze
from utils.validators import validate_all
from controller.input_controller import collect_input_data
from ui.settings_module import create_settings_frame, digit_var, custom_digit_var, mixed_var, english_position_var, fixed_eng_var, fixed_num_var, default_vars, other_vars


def create_input_frame(root, result_frame):
    frame = tk.LabelFrame(root, text="輸入區", font=("Arial", 14))

    # ===== 基本輸入欄位 =====
    name_var = tk.StringVar()
    id_var = tk.StringVar()
    custom_var = tk.StringVar()
    use_name = tk.BooleanVar()
    use_id = tk.BooleanVar()
    use_custom = tk.BooleanVar()

    def on_analyze_click():  #  點擊「分析」按鈕，執行on_analyze_click函數
        # 從 settings_module 導入所有設定變量
        from ui.settings_module import (
            digit_var, custom_digit_var, mixed_var, english_position_var,
            fixed_eng_var, fixed_num_var, default_vars, other_vars
        )

        # 收集輸入資料 (傳入所有設定變量)
        data = collect_input_data(
            name_var, id_var, custom_var, use_name, use_id, use_custom,
            digit_var, custom_digit_var, mixed_var, english_position_var,
            fixed_eng_var, fixed_num_var, default_vars, other_vars
        )# 收集輸入資料
        # data = collect_input_data(name_var, id_var, custom_var, use_name, use_id,
        #                           use_custom)

        errors = validate_all(data)  # 檢查輸入是否合法
        if errors:
            tk.messagebox.showerror("輸入錯誤", "\n".join(errors))
            return  # 停止執行，避免分析錯誤資料
        # 分析輸入資料
        result = analyze(data)

        # 使用結果控制器處理結果 (保存並顯示結果)
        from controller.result_controller import ResultController
        result_controller = ResultController()

        # 定義顯示函數，更新右側結果框架
        def display_result(result_data):
            # 清空現有內容
            for widget in result_frame.winfo_children():
                widget.destroy()

            # 顯示基本結果
            tk.Label(result_frame, text="分析結果：", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                padx=10,
                                                                                pady=(10, 5))

            # 顯示磁場統計
            for k, v in result_data["counts"].items():
                tk.Label(result_frame, text=f"{k}：{v}", anchor="w").pack(anchor="w", padx=20)

            # 顯示推薦數字
            if result_data.get("recommendations"):
                tk.Label(result_frame, text="\n推薦數字：", font=("Arial", 10, "bold")).pack(anchor="w",
                                                                                        padx=10,
                                                                                        pady=(10, 5))
                for num in result_data["recommendations"]:
                    tk.Label(result_frame, text=f"{num}", anchor="w").pack(anchor="w", padx=20)

        # 處理結果 - 這會自動保存分析結果和輸入歷史
        result_controller.process_result(
            result_data=result,
            input_data=data,
            display_callback=display_result
        )

        # 提示用戶分析完成
        tk.messagebox.showinfo("分析完成", "分析已完成，結果已保存到歷史記錄!")
        # result = analyze(data)  # 分析輸入資料，回傳「分析結果」的result

        # # 顯示結果到右側 result_frame
        # for widget in result_frame.winfo_children():
        #     widget.destroy()

        # tk.Label(result_frame, text="分析結果：", font=("Arial", 12, "bold")).pack(anchor="w",
        #                                                                       padx=10,
        #                                                                       pady=(10, 5))
        # for k, v in result["counts"].items():
        #     tk.Label(result_frame, text=f"{k}：{v}", anchor="w").pack(anchor="w", padx=20)

    def on_reset_click():  # 點擊「重置」按鈕，執行on_reset_click函數
        name_var.set("")
        id_var.set("")
        custom_var.set("")
        use_name.set(False)
        use_id.set(False)
        use_custom.set(False)

        digit_var.set("4")
        custom_digit_var.set("")
        mixed_var.set(False)
        english_position_var.set("前")
        fixed_eng_var.set("")
        fixed_num_var.set("")

        for var in default_vars.values():
            var.set(False)
        for var in other_vars.values():
            var.set(False)

    def on_save_settings():  # 點擊「儲存設定」按鈕，執行on_save_settings函數
        try:
            # 確保所有變量都有定義
            from ui.settings_module import (
                digit_var, custom_digit_var, mixed_var, english_position_var,
                fixed_eng_var, fixed_num_var, default_vars, other_vars
            )

            settings = {
                "digit_length": digit_var.get() if digit_var else "4",
                "custom_digit": custom_digit_var.get() if custom_digit_var else "",
                "mix_mode": mixed_var.get() if mixed_var else False,
                "english_position": english_position_var.get() if english_position_var else "前",
                "fixed_eng": fixed_eng_var.get() if fixed_eng_var else "",
                "fixed_num": fixed_num_var.get() if fixed_num_var else "",
                "default_conditions": {
                    k: v.get() for k, v in default_vars.items()
                } if default_vars else {},
                "other_conditions": {
                    k: v.get() for k, v in other_vars.items()
                } if other_vars else {}
            }

            with open("saved_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            tk.messagebox.showinfo("提示", "設定已儲存到 saved_settings.json！")
        except Exception as e:
            # 顯示錯誤訊息
            tk.messagebox.showerror("錯誤", f"儲存設定失敗: {e}")
            # 記錄錯誤
            print(f"儲存設定失敗: {e}")

    # def on_save_settings():  # 點擊「儲存設定」按鈕，執行on_save_settings函數
    #     settings = {
    #         "digit_length": digit_var.get(),
    #         "custom_digit": custom_digit_var.get(),
    #         "mix_mode": mixed_var.get(),
    #         "english_position": english_position_var.get(),
    #         "fixed_eng": fixed_eng_var.get(),
    #         "fixed_num": fixed_num_var.get(),
    #         "default_conditions": {
    #             k: v.get()
    #             for k, v in default_vars.items()
    #         },
    #         "other_conditions": {
    #             k: v.get()
    #             for k, v in other_vars.items()
    #         }
    #     }

    #     with open("saved_settings.json", "w", encoding="utf-8") as f:
    #         json.dump(settings, f, ensure_ascii=False, indent=2)

    #     tk.messagebox.showinfo("提示", "設定已儲存到 saved_settings.json！")

    def load_settings():  # 載入設定
        try:
            with open("saved_settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            digit_var.set(settings.get("digit_length", "4"))
            custom_digit_var.set(settings.get("custom_digit", ""))
            mixed_var.set(settings.get("mix_mode", False))
            english_position_var.set(settings.get("english_position", "前"))
            fixed_eng_var.set(settings.get("fixed_eng", ""))
            fixed_num_var.set(settings.get("fixed_num", ""))

            for key, val in settings.get("default_conditions", {}).items():
                if key in default_vars:
                    default_vars[key].set(val)

            for key, val in settings.get("other_conditions", {}).items():
                if key in other_vars:
                    other_vars[key].set(val)

        except FileNotFoundError:
            pass  # 如果檔案不存在就略過

    load_settings()  # 開啟時自動載入設定

    row = 0
    tk.Checkbutton(frame, text="姓名：", variable=use_name).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=name_var, width=20).grid(row=row,
                                                          column=1,
                                                          columnspan=3,
                                                          sticky="w")

    row += 1
    tk.Checkbutton(frame, text="身分證：", variable=use_id).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=id_var, width=20).grid(row=row, column=1, columnspan=3, sticky="w")

    row += 1
    tk.Checkbutton(frame, text="自定義：", variable=use_custom).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=custom_var, width=20).grid(row=row,
                                                            column=1,
                                                            columnspan=3,
                                                            sticky="w")

    # ===== 插入設定條件模組 =====
    row += 1
    settings_frame = create_settings_frame(frame)
    settings_frame.grid(row=row, column=0, columnspan=4, pady=10)

    # ===== 按鈕列 =====
    row += 1
    tk.Button(frame, text="分析", command=on_analyze_click).grid(row=row, column=0, pady=5)
    tk.Button(frame, text="重置", command=on_reset_click).grid(row=row, column=1, pady=5)
    tk.Button(frame, text="儲存設定", command=on_save_settings).grid(row=row, column=2, pady=5)

    return frame
