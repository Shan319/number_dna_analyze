#  ui/settings_module.py

import tkinter as tk

digit_var = None
custom_digit_var = None
mixed_var = None
english_position_var = None
fixed_eng_var = None
fixed_num_var = None
default_vars = {}
other_vars = {}


def create_collapsible_magnetic_info(parent_frame):
    """可折疊的磁場資訊面板"""

    # 狀態變數
    info_visible = tk.BooleanVar(value=False)  # 默認隱藏

    def toggle_info():
        """切換資訊顯示/隱藏"""
        if info_visible.get():
            info_frame.grid_remove()
            toggle_btn.config(text="▶ 顯示磁場說明")
            info_visible.set(False)
        else:
            info_frame.grid()
            toggle_btn.config(text="▼ 隱藏磁場說明")
            info_visible.set(True)

    # 切換按鈕
    toggle_btn = tk.Button(parent_frame,
                           text="▶ 顯示磁場說明",
                           command=toggle_info,
                           font=("Arial", 9),
                           relief="flat",
                           fg="blue",
                           cursor="hand2")
    toggle_btn.grid(row=6, column=0, sticky="w", pady=(10, 5))

    # 資訊內容區域（初始隱藏）
    info_frame = tk.Frame(parent_frame, relief="sunken", bd=1)
    info_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0, 5))
    info_frame.grid_columnconfigure(0, weight=1)
    info_frame.grid_columnconfigure(1, weight=1)
    info_frame.grid_remove()  # 初始隱藏

    # 創建磁場說明內容
    create_magnetic_layout_content(info_frame)


def create_magnetic_layout_content(info_frame):
    """在指定frame中創建磁場說明內容"""

    # 左側吉星
    left_frame = tk.Frame(info_frame)
    left_frame.grid(row=0, column=0, sticky="nw", padx=(10, 5), pady=10)

    tk.Label(left_frame, text="✦ 吉星磁場 ✦", font=("Arial", 10, "bold"),
             fg="darkgreen").pack(anchor="w")

    good_fields = ["延年: 主和諧、執行力、開業", "天醫: 主健康、貴人、智慧", "生氣: 主人緣、平安、進步", "伏位: 主平靜、潛力、耐心"]

    for field in good_fields:
        tk.Label(left_frame, text=field, font=("Arial", 10), fg="green").pack(anchor="w")

    # 右側凶星
    right_frame = tk.Frame(info_frame)
    right_frame.grid(row=0, column=1, sticky="nw", padx=(5, 10), pady=10)

    tk.Label(right_frame, text="✦ 凶星磁場 ✦", font=("Arial", 10, "bold"),
             fg="darkred").pack(anchor="w")

    bad_fields = ["絕命: 大凶，破財、衝動、劫難", "五鬼: 中凶，主變動、小人、災厄", "六煞: 凶星，意外、失財、爛桃花", "禍害: 小凶，口舌、意外、疾病"]

    for field in bad_fields:
        tk.Label(right_frame, text=field, font=("Arial", 10), fg="red").pack(anchor="w")


def create_settings_frame(root):
    global digit_var, custom_digit_var, mixed_var, english_position_var, fixed_eng_var
    global fixed_num_var, default_vars, other_vars

    digit_var = tk.StringVar(value="4")
    custom_digit_var = tk.StringVar()
    mixed_var = tk.BooleanVar()
    english_position_var = tk.StringVar(value="前")
    fixed_eng_var = tk.StringVar()
    fixed_num_var = tk.StringVar()

    default_vars = {name: tk.BooleanVar() for name in ["絕命", "五鬼", "六煞", "禍害"]}
    other_vars = {name: tk.BooleanVar() for name in ["延年", "天醫", "生氣", "伏位"]}

    frame = tk.LabelFrame(root, text="生成條件設定", font=("Arial", 12), padx=10, pady=10)

    tk.Label(frame, text="總位數：").grid(row=0, column=0, sticky="w")
    digits = [("4", "4"), ("6", "6"), ("8", "8"), ("自訂", "custom")]
    for i, (label, val) in enumerate(digits):
        tk.Radiobutton(frame, text=label, variable=digit_var, value=val).grid(row=0,
                                                                              column=i + 1,
                                                                              sticky="w")
    tk.Entry(frame, textvariable=custom_digit_var, width=5).grid(row=0, column=5, sticky="w")

    tk.Checkbutton(frame, text="添加固定選項", variable=mixed_var).grid(row=1, column=0, sticky="w")
    tk.Label(frame, text="固定位置：").grid(row=2, column=0, sticky="w")
    tk.Radiobutton(frame, text="前", variable=english_position_var, value="前").grid(row=2,
                                                                                   column=1,
                                                                                   sticky="w")
    tk.Radiobutton(frame, text="中", variable=english_position_var, value="中").grid(row=2,
                                                                                   column=2,
                                                                                   sticky="w")
    tk.Radiobutton(frame, text="後", variable=english_position_var, value="後").grid(row=2,
                                                                                   column=3,
                                                                                   sticky="w")

    tk.Label(frame, text="固定英文或數字：").grid(row=3, column=0, sticky="w")
    tk.Entry(frame, textvariable=fixed_num_var, width=10).grid(row=3, column=1, sticky="w")

    tk.Label(frame, text="默認條件：", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w")
    for i, text in enumerate(default_vars):
        button = tk.Checkbutton(frame, text=f"抵消{text}", variable=default_vars[text])
        button.grid(row=4, column=i + 1, sticky="w")

    tk.Label(frame, text="其他條件：", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w")
    for i, text in enumerate(other_vars):
        tk.Checkbutton(frame, text=f"增加{text}", variable=other_vars[text]).grid(row=5,
                                                                                column=i + 1,
                                                                                sticky="w")

    create_collapsible_magnetic_info(frame)
    # tk.Label(frame, text="[簡述不同條件代表的意義]", font=("Arial", 9), fg="gray").grid(row=6,
    #                                                                          column=0,
    #                                                                          columnspan=4,
    #                                                                          sticky="w",
    #                                                                          pady=(5, 0))

    return frame
