# ui/input_module.py

import tkinter as tk
from ui.settings_module import create_settings_frame
from controller.input_controller import collect_input_data, analyze_input

def create_input_frame(root, result_frame):
    frame = tk.LabelFrame(root, text="輸入區", font=("Arial", 14))

    # ===== 基本輸入欄位 =====
    name_var = tk.StringVar()
    id_var = tk.StringVar()
    custom_var = tk.StringVar()
    use_name = tk.BooleanVar()
    use_id = tk.BooleanVar()
    use_custom = tk.BooleanVar()

    def on_analyze_click():
        data = collect_input_data(name_var, id_var, custom_var, use_name, use_id, use_custom)
        result = analyze_input(data)

        # 顯示結果到右側 result_frame
        for widget in result_frame.winfo_children():
            widget.destroy()

        tk.Label(result_frame, text="分析結果：", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        for k, v in result["counts"].items():
            tk.Label(result_frame, text=f"{k}：{v}", anchor="w").pack(anchor="w", padx=20)

    row = 0
    tk.Checkbutton(frame, text="姓名：", variable=use_name).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=name_var, width=20).grid(row=row, column=1, columnspan=3, sticky="w")

    row += 1
    tk.Checkbutton(frame, text="身分證：", variable=use_id).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=id_var, width=20).grid(row=row, column=1, columnspan=3, sticky="w")

    row += 1
    tk.Checkbutton(frame, text="自定義：", variable=use_custom).grid(row=row, column=0, sticky="w")
    tk.Entry(frame, textvariable=custom_var, width=20).grid(row=row, column=1, columnspan=3, sticky="w")

    # ===== 插入設定條件模組 =====
    row += 1
    settings_frame = create_settings_frame(frame)
    settings_frame.grid(row=row, column=0, columnspan=4, pady=10)

    # ===== 按鈕列 =====
    row += 1
    tk.Button(frame, text="分析", command=on_analyze_click).grid(row=row, column=0, pady=5)
    tk.Button(frame, text="重置").grid(row=row, column=1, pady=5)
    tk.Button(frame, text="儲存設定").grid(row=row, column=2, pady=5)

    return frame
