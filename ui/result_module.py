# ui/result_module.py
"""
數字DNA分析器 - 結果顯示模組
負責展示分析結果並提供結果互動功能

功能:
1. 顯示磁場分析的基本統計結果
2. 展示進階規則應用後的調整結果
3. 顯示推薦的幸運數字
4. 提供保存/載入分析結果的界面
5. 支援不同顯示模式的切換
"""
from collections import Counter
import logging
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from data.result_data import ResultData, FieldDetail
from ui.display_module import show_field_visualization
from controller.analysis_controller import generate_lucky_numbers
from core.field_analyzer import analyze_input
from core.number_analyzer import keyword_fields

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.ResultModule")


class ResultView:

    def __init__(self, parent: tk.Widget) -> None:
        logger.info("創建結果顯示框架")

        self.parent = parent
        self.frame = tk.LabelFrame(parent, text="分析結果", font=("Arial", 14))
        self.input_data: ResultData | None = None
        self.result_data: ResultData | None = None

        self.notbook: ttk.Notebook | None = None
        self.basic_tab: ttk.Frame | None = None
        self.advanced_tab: ttk.Frame | None = None
        self.lucky_tab: ttk.Frame | None = None
        self.lucky_tree_view: ttk.Treeview | None = None
        self.details_tab: ttk.Frame | None = None
        self.detail_tree_view: ttk.Treeview | None = None

        self.update_display()

    def update_display(self):
        """更新畫面

        注意先賦值 self.input_data/self.result_data 再呼叫 update_display。
        """

        # 清空現有內容
        for widget in self.frame.winfo_children():
            widget.destroy()

        if self.result_data is None:
            # 初始資訊標籤
            initial_label = tk.Label(self.frame,
                                     text="請在左側輸入資料並點選「分析」按鈕",
                                     font=("Arial", 12),
                                     padx=20,
                                     pady=20)
            initial_label.pack(expand=True)
        else:
            result_data = self.result_data
            input_type = result_data.input_data.input_type
            logger.info(f"更新結果顯示: {input_type.value}")

            # 分析類型標頭
            header = tk.Label(self.frame,
                              text=f"分析類型: {input_type.value}",
                              font=("Arial", 12, "bold"),
                              anchor="w")
            header.pack(fill="x", padx=10, pady=(10, 5))

            # 使用Notebook創建選項卡界面
            notebook = ttk.Notebook(self.frame)
            self.notebook = notebook
            notebook.pack(fill="both", expand=True, padx=10, pady=5)

            # 基本統計選項卡
            basic_tab = ttk.Frame(notebook)
            self.basic_tab = basic_tab
            notebook.add(basic_tab, text="基本統計")
            self._create_basic_tab(basic_tab, result_data)

            # 進階分析選項卡
            advanced_tab = ttk.Frame(notebook)
            self.advanced_tab = advanced_tab
            notebook.add(advanced_tab, text="進階分析")
            self._create_advanced_tab(advanced_tab, result_data)

            # 幸運數字選項卡
            lucky_tab = ttk.Frame(notebook)
            self.lucky_tab = lucky_tab
            notebook.add(lucky_tab, text="幸運數字")
            self._create_lucky_tab(lucky_tab, result_data)

            # 磁場詳情選項卡
            details_tab = ttk.Frame(notebook)
            self.details_tab = details_tab
            notebook.add(details_tab, text="磁場詳情")
            self._create_details_tab(details_tab, result_data)

    def _create_basic_tab(self, tab: ttk.Frame, result_data: ResultData):
        """創建基本統計選項卡"""

        # 原始磁場統計
        tk.Label(tab, text="原始磁場統計", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                      padx=5,
                                                                      pady=(10, 5))

        counts_frame = tk.Frame(tab)
        counts_frame.pack(fill="x", padx=10)

        row, col = 0, 0
        for field, count in result_data.counts.items():
            field_label = tk.Label(counts_frame, text=f"{field}: {count}", width=15, anchor="w")
            field_label.grid(row=row, column=col, sticky="w", padx=5, pady=2)

            col += 1
            if col > 2:  # 每行3個項目
                col = 0
                row += 1

        # 原始磁場序列
        if result_data.raw_analysis:
            tk.Label(tab, text="磁場序列", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                        padx=5,
                                                                        pady=(15, 5))

            sequence_frame = tk.Frame(tab)
            sequence_frame.pack(fill="x", padx=10, pady=5)

            sequence_text = tk.Text(sequence_frame, height=3, width=40, wrap="word")
            sequence_text.insert("1.0", result_data.raw_analysis)
            sequence_text.config(state="disabled")
            sequence_text.pack(fill="x")

    def _create_advanced_tab(self, tab: ttk.Frame, result_data: ResultData):
        """創建進階分析選項卡"""
        # 調整日誌
        if result_data.adjusted_log:
            tk.Label(tab, text="進階調整規則應用", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                            padx=5,
                                                                            pady=(10, 5))

            log_frame = tk.Frame(tab)
            log_frame.pack(fill="x", padx=10, pady=5)

            log_text = tk.Text(log_frame, height=4, width=40, wrap="word")
            log_text.insert("1.0", " ".join(result_data.adjusted_log))
            log_text.config(state="disabled")
            log_text.pack(fill="x")
        else:
            tk.Label(tab, text="無進階調整規則被應用", font=("Arial", 11)).pack(anchor="w",
                                                                      padx=15,
                                                                      pady=(10, 5))

        # 調整後磁場統計
        tk.Label(tab, text="調整後磁場統計", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                       padx=5,
                                                                       pady=(15, 5))

        adjusted_frame = tk.Frame(tab)
        adjusted_frame.pack(fill="x", padx=10)

        row, col = 0, 0
        for field, count in result_data.adjusted_counts.items():
            field_label = tk.Label(adjusted_frame, text=f"{field}: {count}", width=15, anchor="w")
            field_label.grid(row=row, column=col, sticky="w", padx=5, pady=2)

            col += 1
            if col > 2:  # 每行3個項目
                col = 0
                row += 1

        # 磁場吉凶統計
        pos_fields = ['天醫', '生氣', '延年', '伏位']
        neg_fields = ['五鬼', '六煞', '禍害', '絕命']

        adjusted_counts = result_data.adjusted_counts
        pos_count = sum(adjusted_counts.get(f, 0) for f in pos_fields)
        neg_count = sum(adjusted_counts.get(f, 0) for f in neg_fields)
        total_count = pos_count + neg_count

        tk.Label(tab, text="磁場能量分布", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                      padx=5,
                                                                      pady=(15, 5))

        stats_frame = tk.Frame(tab)
        stats_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(stats_frame,
                 text=f"吉星磁場: {pos_count} ({pos_count / total_count * 100:.1f}%)"
                 if total_count else "吉星磁場: 0 (0%)",
                 width=25,
                 anchor="w").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(stats_frame,
                 text=f"凶星磁場: {neg_count} ({neg_count / total_count * 100:.1f}%)"
                 if total_count else "凶星磁場: 0 (0%)",
                 width=25,
                 anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=2)

    def _create_lucky_tab(self, tab: ttk.Frame, result_data: ResultData):
        """創建幸運數字選項卡"""
        # 清空現有內容（用於更新時）
        for widget in tab.winfo_children():
            widget.destroy()

        recommendations = result_data.recommendations

        if recommendations:
            tk.Label(tab, text="推薦幸運數字", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                          padx=5,
                                                                          pady=(10, 5))

            frame = tk.Frame(tab)
            frame.pack(fill="both", expand=True, padx=10, pady=5)

            tk.Label(frame, text="雙擊數字可查看詳情", anchor="w").pack(anchor="w", pady=(0, 5))

            # 創建 Treeview
            columns = ("編號", "幸運數字")
            lucky_tree_view = ttk.Treeview(frame, columns=columns, show="headings", height=10)
            self.lucky_tree_view = lucky_tree_view
            lucky_tree_view.pack(side="left", fill="both", expand=True)

            # 設定標題列
            for col in columns:
                lucky_tree_view.heading(col, text=col)
            lucky_tree_view.column("編號", width=22)

            # 填充數據
            for i, num in enumerate(recommendations, 1):
                lucky_tree_view.insert("", tk.END, values=(f"{i}", f"{num}"))

            # 添加滾動條
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=lucky_tree_view.yview)
            scrollbar.pack(side="right", fill="y")
            lucky_tree_view.config(yscrollcommand=scrollbar.set)

            # 連點兩下選查看詳情功能
            lucky_tree_view.bind("<Double-1>", self._on_lucky_tree_view_double_clicked)

            generate_btn = tk.Button(tab, text="生成更多幸運數字", command=self._on_generate_btn_clicked)
            generate_btn.pack(pady=10)
        else:
            tk.Label(tab, text="沒有可用的幸運數字推薦", font=("Arial", 11)).pack(expand=True, pady=20)

    def _on_lucky_tree_view_double_clicked(self, event: tk.Event):
        if self.lucky_tree_view is None:
            return
        if self.result_data is None:
            return

        # 取得滑鼠所在位置對應的 item
        item = self.lucky_tree_view.identify_row(event.y)
        if item:
            index = self._get_index(self.lucky_tree_view, item)
            number_text = self.result_data.recommendations[index]
            self._lucky_number_popup(number_text)

    def _lucky_number_popup(self, number_text: str):
        # 創建彈出窗口
        popup = tk.Toplevel()
        popup.title(f"幸運數字詳情: {number_text}")
        popup.geometry("400x300")

        # 數字顯示
        tk.Label(popup, text=number_text, font=("Courier", 24, "bold")).pack(pady=(20, 10))

        # 數位分析
        tk.Label(popup, text="磁場分析", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                      padx=20,
                                                                      pady=(10, 5))

        digit_frame = tk.Frame(popup)
        digit_frame.pack(fill="x", padx=20, pady=5)

        # 分析幸運數字的磁場組合
        result = analyze_input(number_text)
        tk.Label(digit_frame, text=f"磁場組合：{result} ", anchor="w").pack(anchor="w")

        result_key = result.split()
        base_counts = Counter(result_key)
        for field, count in base_counts.items():
            keywords = "、".join(keyword_fields.get(field, []))  # 取得關鍵字集合並轉成字串
            tk.Label(digit_frame, text=f"{field}：{keywords} ", anchor="w").pack(anchor="w")

        # [TODO] 這裡應該調用數字分析引擎的函數來分析數字，這裡只是簡單示例
        tk.Label(popup, text="由伏位、天醫、生氣和延年磁場組成", wraplength=350).pack(anchor="w", padx=30)

        # 複製按鈕
        tk.Button(popup, text="複製到剪貼簿",
                  command=lambda: self._on_copy_btn_clicked(number_text)).pack(pady=15)

    def _on_copy_btn_clicked(self, text):
        """複製文本到剪貼簿"""
        self.frame.clipboard_clear()
        self.frame.clipboard_append(text)
        messagebox.showinfo("成功", "已複製到剪貼簿!")

    def _on_generate_btn_clicked(self):
        """生成更多推薦數字並更新數據和UI"""

        if self.lucky_tab is None:
            return
        if self.result_data is None:
            return

        # 詢問要生成的數量
        count = simpledialog.askinteger("輸入",
                                        "請輸入要生成的幸運數字數量:",
                                        initialvalue=5,
                                        minvalue=1,
                                        maxvalue=20)
        if not count:
            return

        # 獲取當前的磁場計數
        adjusted_counts = self.result_data.adjusted_counts

        # 更新用_獲取當前的數字長度_從現有推薦數字推斷
        existing_recommendations = self.result_data.recommendations
        if existing_recommendations:
            digit_length = len(str(existing_recommendations[0]))
        else:
            digit_length = 4

        # 生成新的幸運數字
        new_numbers = generate_lucky_numbers(adjusted_counts, digit_length, count)
        if new_numbers:
            # 更新結果數據
            self.result_data.recommendations = new_numbers

            # 顯示更新成功
            messagebox.showinfo("成功", f"已生成 {len(new_numbers)} 個新的幸運數字")
            self._create_lucky_tab(self.lucky_tab, result_data=self.result_data)  # 遞歸重新創建

    def _create_details_tab(self, tab: ttk.Frame, result_data: ResultData):
        """創建磁場詳情選項卡"""
        field_details = result_data.field_details

        if field_details:
            tk.Label(tab, text="磁場詳細資訊", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                          padx=5,
                                                                          pady=(10, 5))

            frame = tk.Frame(tab)
            frame.pack(fill="both", expand=True, padx=10, pady=5)

            # 說明文字
            tk.Label(frame, text="雙擊磁場可查看詳細資訊", anchor="w").pack(anchor="w", pady=(0, 5))

            # 創建 Treeview
            columns = ("磁場", "出現次數", "關鍵字")
            tree_view = ttk.Treeview(frame, columns=columns, show="headings", height=6)
            self.detail_tree_view = tree_view

            # 設定標題列
            for col in columns:
                tree_view.heading(col, text=col)
            tree_view.column("磁場", width=50)
            tree_view.column("出現次數", width=100)

            # 填充數據
            for field, details in field_details.items():
                keywords: str | list[str] = details.keywords
                if isinstance(keywords, list):
                    keywords = "、".join(keywords)

                tree_view.insert("", "end", values=(field, details.count, keywords))

            # 添加滾動條
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=tree_view.yview)
            scrollbar.pack(side="right", fill="y")
            tree_view.config(yscrollcommand=scrollbar.set)
            tree_view.pack(side="left", fill="both", expand=True)

            # 連點兩下選查看詳情功能
            tree_view.bind("<Double-1>", self._on_details_tree_view_double_clicked)

        else:
            tk.Label(tab, text="沒有可用的磁場詳細資訊", font=("Arial", 11)).pack(expand=True, pady=20)

    def _on_details_tree_view_double_clicked(self, event: tk.Event):
        if self.detail_tree_view is None:
            return
        if self.result_data is None:
            return

        # 取得滑鼠所在位置對應的 item
        item = self.detail_tree_view.identify_row(event.y)
        if item:
            index = self._get_index(self.detail_tree_view, item)

            field_name, details = list(self.result_data.field_details.items())[index]
            self._show_field_details_popup(field_name, details)

    def _show_field_details_popup(self, field_name: str, details: FieldDetail):
        """在彈出窗口中顯示磁場詳細資訊"""

        # 創建彈出窗口
        popup = tk.Toplevel()
        popup.title(f"{field_name} 磁場詳細資訊")
        popup.geometry("450x500")
        popup.resizable(False, False)

        # 關鍵字
        keywords: str | list[str] = details.keywords
        if isinstance(keywords, list):
            keywords = "、".join(keywords)

        tk.Label(popup, text="關鍵字:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                      padx=20,
                                                                      pady=(20, 0))
        tk.Label(popup, text=keywords, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

        # 優勢
        strengths = details.strengths
        strengths = strengths if strengths else "無資料"
        tk.Label(popup, text="優勢:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                     padx=20,
                                                                     pady=(10, 0))

        tk.Label(popup, text=strengths, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

        # 弱點
        weaknesses = details.weaknesses
        weaknesses = weaknesses if weaknesses else "無資料"
        tk.Label(popup, text="弱點:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                     padx=20,
                                                                     pady=(10, 0))
        tk.Label(popup, text=weaknesses, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

        # 財務建議
        financial = details.financial_strategy
        financial = financial if financial else "無資料"
        tk.Label(popup, text="財務建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                       padx=20,
                                                                       pady=(10, 0))
        tk.Label(popup, text=financial, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

        # 關係建議
        relationship = details.relationship_advice
        relationship = relationship if relationship else "無資料"
        tk.Label(popup, text="關係建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                       padx=20,
                                                                       pady=(10, 0))
        tk.Label(popup, text=relationship, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

        # 確認按鈕
        tk.Button(popup, text="確定", command=popup.destroy).pack(pady=20)

    def _create_visualization_tab(self, tab: ttk.Frame, result_data: ResultData):
        """顯示磁場能量視覺化"""

        tk.Label(tab, text="磁場能量視覺化", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                       padx=5,
                                                                       pady=(10, 5))

        fields_frame = tk.Frame(tab)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=5)
        show_field_visualization(result_data)

    def _get_index(self, tree_view: ttk.Treeview, item: str):
        """回覆該 item 是第幾筆資料"""
        all_items = tree_view.get_children()
        index = all_items.index(item)
        return index
