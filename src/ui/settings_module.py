#  ui/settings_module.py

import tkinter as tk

from src.data.input_data import InputData, FixDigitsPosition


class SettingView:

    def __init__(self, parent: tk.Widget) -> None:
        """設定畫面模組。

        Parameters
        ----------
        parent : tk.Widget
            設定畫面放置的父畫面
        """
        self.digits_length_var = tk.StringVar(value="4")
        self.custom_digits_length_var = tk.StringVar()
        self.fixed_position_var = tk.StringVar(value="不添加")
        self.fixed_value_var = tk.StringVar()
        self.default_vars = {name: tk.BooleanVar() for name in ["絕命", "五鬼", "六煞", "禍害"]}
        self.other_vars = {name: tk.BooleanVar() for name in ["延年", "天醫", "生氣", "伏位"]}

        frame = tk.LabelFrame(parent, text="生成條件設定", font=("Arial", 12), padx=10, pady=10)
        self.frame = frame

        # 生成總位數
        row = 0
        tk.Label(frame, text="生成總位數：").grid(row=0, column=0, sticky="w")
        digits = [("4", "4"), ("6", "6"), ("8", "8"), ("自訂", "custom")]
        for i, (label, val) in enumerate(digits):
            tk.Radiobutton(frame, text=label, variable=self.digits_length_var,
                           value=val).grid(row=0, column=i + 1, sticky="w")
        tk.Entry(frame, textvariable=self.custom_digits_length_var, width=5).grid(row=row,
                                                                                  column=5,
                                                                                  sticky="w")

        # 添加固定英數字
        row += 1
        add_fixed_digits_info = [(FixDigitsPosition.NONE), (FixDigitsPosition.BEGIN),
                                 (FixDigitsPosition.CENTER), (FixDigitsPosition.END)]
        tk.Label(frame, text="添加固定英數字：").grid(row=row, column=0, sticky="w")
        for column, position in enumerate(add_fixed_digits_info, 1):
            text = position.value
            tk.Radiobutton(frame, text=text, variable=self.fixed_position_var,
                           value=text).grid(row=row, column=column, sticky="w")

        row += 1
        tk.Label(frame, text="固定英數字：").grid(row=row, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.fixed_value_var, width=10).grid(row=row,
                                                                          column=1,
                                                                          sticky="w")

        row += 1
        tk.Label(frame, text="默認條件：", font=("Arial", 12, "bold")).grid(row=row,
                                                                       column=0,
                                                                       sticky="w")
        for i, text in enumerate(self.default_vars):
            button = tk.Checkbutton(frame, text=f"抵消{text}", variable=self.default_vars[text])
            button.grid(row=row, column=i + 1, sticky="w")
            self.default_vars[text].set(True)

        row += 1
        tk.Label(frame, text="其他條件：", font=("Arial", 12, "bold")).grid(row=row,
                                                                       column=0,
                                                                       sticky="w")
        for i, text in enumerate(self.other_vars):
            tk.Checkbutton(frame, text=f"增加{text}",
                           variable=self.other_vars[text]).grid(row=row, column=i + 1, sticky="w")

        self.reset_settings()
        self.create_collapsible_magnetic_info(frame)

    def create_collapsible_magnetic_info(self, parent_frame):
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

    def create_magnetic_layout_content(self, info_frame: tk.Widget):
        """在指定 frame 中創建磁場說明內容"""

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

    def reset_settings(self):
        """重設畫面。"""
        input_data = InputData.get_defaults()
        self.load_settings(input_data)

    def load_settings(self, input_data: InputData):
        """依照 input_data 載入設定畫面上的值。

        Parameters
        ----------
        input_data : InputData
            設定資料
        """

        if input_data.is_custom_digits_length:
            self.digits_length_var.set("custom")
            self.custom_digits_length_var.set(str(input_data.digits_length))
        else:
            self.digits_length_var.set(str(input_data.digits_length))
            self.custom_digits_length_var.set("")

        self.fixed_position_var.set(input_data.fixed_digits_position.value)
        self.fixed_value_var.set(input_data.fixed_digits_value)

        for key, val in input_data.default_conditions.items():
            if key in self.default_vars:
                self.default_vars[key].set(val)

        for key, val in input_data.other_conditions.items():
            if key in self.other_vars:
                self.other_vars[key].set(val)

    def dump_settings(self) -> InputData:
        """將畫面上的設定值倒出成 InputData

        注意這個值不包含 input_type 和 input_value

        Returns
        -------
        InputData
            依照畫面上的設定值變成的 InputData
        """
        # 讀取數字位數限制
        digit_value = self.digits_length_var.get()
        is_custom_digits_length = digit_value == "custom"
        if is_custom_digits_length:
            digits = (self.custom_digits_length_var.get().strip())
        else:
            digits = (digit_value)

        # 讀取固定英數字
        english_position = self.fixed_position_var.get()
        fixed_digits_position = FixDigitsPosition(english_position)
        fixed_digits_value = self.fixed_value_var.get().strip()

        default_conditions: dict[str, bool] = {}
        other_conditions: dict[str, bool] = {}

        for k, v in self.default_vars.items():
            default_conditions[k] = v.get()

        for k, v in self.other_vars.items():
            other_conditions[k] = v.get()

        input_data = InputData(digits_length=digits,
                               is_custom_digits_length=is_custom_digits_length,
                               fixed_digits_position=fixed_digits_position,
                               fixed_digits_value=fixed_digits_value,
                               default_conditions=default_conditions,
                               other_conditions=other_conditions)
        return input_data
