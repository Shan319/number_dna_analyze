#  settings_module.py

import tkinter as tk

digit_var = None
custom_digit_var = None
mixed_var = None
english_position_var = None
fixed_eng_var = None
fixed_num_var = None
default_vars = {}
other_vars = {}

def create_settings_frame(root):
    global digit_var, custom_digit_var, mixed_var, english_position_var, fixed_eng_var, fixed_num_var, default_vars, other_vars

    digit_var = tk.StringVar(value="4")
    custom_digit_var = tk.StringVar()
    mixed_var = tk.BooleanVar()
    english_position_var = tk.StringVar(value="前")
    fixed_eng_var = tk.StringVar()
    fixed_num_var = tk.StringVar()

    default_vars = {name: tk.BooleanVar() for name in ["五鬼", "六煞", "禍害", "絕命"]}
    other_vars = {name: tk.BooleanVar() for name in ["天醫", "生氣", "延年"]}

    frame = tk.LabelFrame(root, text="生成條件設定", font=("Arial", 12))

    tk.Label(frame, text="數字位數：").grid(row=0, column=0, sticky="w")
    digits = [("4", "4"), ("6", "6"), ("8", "8"), ("自訂", "custom")]
    for i, (label, val) in enumerate(digits):
        tk.Radiobutton(frame, text=label, variable=digit_var, value=val).grid(row=0, column=i+1, sticky="w")
    tk.Entry(frame, textvariable=custom_digit_var, width=5).grid(row=0, column=5, sticky="w")

    tk.Checkbutton(frame, text="英數混合", variable=mixed_var).grid(row=1, column=0, sticky="w")
    tk.Radiobutton(frame, text="英文在前", variable=english_position_var, value="前").grid(row=1, column=1, sticky="w")
    tk.Radiobutton(frame, text="英文在中", variable=english_position_var, value="中").grid(row=1, column=2, sticky="w")
    tk.Radiobutton(frame, text="英文在後", variable=english_position_var, value="後").grid(row=1, column=3, sticky="w")

    tk.Label(frame, text="固定英文：").grid(row=2, column=0, sticky="w")
    tk.Entry(frame, textvariable=fixed_eng_var, width=10).grid(row=2, column=1, sticky="w")
    tk.Label(frame, text="固定數字：").grid(row=3, column=0, sticky="w")
    tk.Entry(frame, textvariable=fixed_num_var, width=10).grid(row=3, column=1, sticky="w")

    tk.Label(frame, text="默認條件：", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w")
    for i, text in enumerate(default_vars):
        tk.Checkbutton(frame, text=f"抵消{text}", variable=default_vars[text]).grid(row=4, column=i+1, sticky="w")

    tk.Label(frame, text="其他條件：", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w")
    for i, text in enumerate(other_vars):
        tk.Checkbutton(frame, text=f"增加{text}", variable=other_vars[text]).grid(row=5, column=i+1, sticky="w")

    tk.Label(
        frame,
        text="[簡述不同條件代表的意義]",
        font=("Arial", 9),
        fg="gray"
    ).grid(row=6, column=0, columnspan=4, sticky="w", pady=(5, 0))

    return frame
