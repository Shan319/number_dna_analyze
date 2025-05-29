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
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import logging
import os
from functools import partial

from data.result_data import ResultData
from core.field_analyzer import analyze_input
from core.number_analyzer import keyword_fields

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.ResultModule")


def create_result_content(parent: tk.Frame, result_data: ResultData | None):
    """
    創建結果顯示框架

    Args:
        parent frame

    Returns:
        frame: 結果顯示框架
    """
    logger.info("創建結果顯示框架")

    # frame = tk.Frame(parent)
    frame = tk.LabelFrame(parent, text="分析結果", font=("Arial", 14))
    if result_data is None:
        # 創建主框架

        # 初始資訊標籤
        initial_label = tk.Label(frame,
                                 text="請在左側輸入資料並點選「分析」按鈕",
                                 font=("Arial", 12),
                                 padx=20,
                                 pady=20)
        initial_label.pack(expand=True)
    else:
        update_display(frame, result_data)

    return frame


def update_display(frame: tk.Widget, result_data: ResultData | None):
    """
    更新結果顯示內容

    Args:
        frame: 結果顯示框架
        result_data: 分析結果數據
    """
    if not result_data:
        logger.warning("接收到空的分析結果")
        return

    input_type = result_data.input_type
    logger.info(f"更新結果顯示: {input_type.value}")

    # 清空現有內容
    for widget in frame.winfo_children():
        widget.destroy()

    # 分析類型標頭
    header = tk.Label(frame,
                      text=f"分析類型: {input_type.value}",
                      font=("Arial", 12, "bold"),
                      anchor="w")
    header.pack(fill="x", padx=10, pady=(10, 5))

    # 使用Notebook創建選項卡界面
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)

    # 基本統計選項卡
    basic_tab = ttk.Frame(notebook)
    notebook.add(basic_tab, text="基本統計")
    create_basic_tab(basic_tab, result_data)

    # 進階分析選項卡
    advanced_tab = ttk.Frame(notebook)
    notebook.add(advanced_tab, text="進階分析")
    create_advanced_tab(advanced_tab, result_data)

    # 幸運數字選項卡
    lucky_tab = ttk.Frame(notebook)
    notebook.add(lucky_tab, text="幸運數字")
    create_lucky_tab(lucky_tab, result_data)

    # 磁場詳情選項卡
    details_tab = ttk.Frame(notebook)
    notebook.add(details_tab, text="磁場詳情")
    create_details_tab(details_tab, result_data)


def create_basic_tab(tab: ttk.Frame, result_data: ResultData):
    """創建基本統計選項卡"""
    # 原始磁場統計
    tk.Label(tab, text="原始磁場統計", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=(10, 5))

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


def create_advanced_tab(tab: ttk.Frame, result_data: ResultData):
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
        tk.Label(tab, text="無進階調整規則被應用", font=("Arial", 11)).pack(anchor="w", padx=15, pady=(10, 5))

    # 調整後磁場統計
    tk.Label(tab, text="調整後磁場統計", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=(15, 5))

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

    tk.Label(tab, text="磁場能量分布", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=(15, 5))

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


def create_lucky_tab(tab: ttk.Frame, result_data: ResultData):
    """創建幸運數字選項卡"""
    # 清空現有內容（用於更新時）
    for widget in tab.winfo_children():
        widget.destroy()

    recommendations = result_data.recommendations

    if recommendations:
        tk.Label(tab, text="推薦幸運數字", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                      padx=5,
                                                                      pady=(10, 5))

        # 幸運數字列表
        lucky_frame = tk.Frame(tab)
        lucky_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 使用Listbox顯示幸運數字
        tk.Label(lucky_frame, text="點選數字可查看詳情:", anchor="w").pack(anchor="w", pady=(0, 5))

        lucky_list = tk.Listbox(lucky_frame, height=10, width=30, font=("Courier", 12))
        lucky_list.pack(side="left", fill="both", expand=True)

        # 添加滾動條
        scrollbar = tk.Scrollbar(lucky_frame, orient="vertical", command=lucky_list.yview)
        scrollbar.pack(side="right", fill="y")
        lucky_list.config(yscrollcommand=scrollbar.set)

        # 填充幸運數字
        for i, num in enumerate(recommendations, 1):
            lucky_list.insert(tk.END, f"{i}. {num}")

        # 點選查看詳情功能
        lucky_list.bind("<Double-1>",
                        lambda e: show_number_detail(lucky_list.get(lucky_list.curselection())))

        # 支援更新推薦數字生成
        def refresh_numbers():
            new_data = generate_more_numbers_and_update(result_data)
            if new_data:
                create_lucky_tab(tab, new_data)  # 遞歸重新創建

        generate_btn = tk.Button(tab, text="生成更多幸運數字", command=refresh_numbers)
        generate_btn.pack(pady=10)
    else:
        tk.Label(tab, text="沒有可用的幸運數字推薦", font=("Arial", 11)).pack(expand=True, pady=20)


def create_details_tab(tab: ttk.Frame, result_data: ResultData):
    """創建磁場詳情選項卡"""
    field_details = result_data.field_details

    if field_details:
        # 使用Treeview顯示磁場列表
        tk.Label(tab, text="磁場詳細資訊", font=("Arial", 11, "bold")).pack(anchor="w",
                                                                      padx=5,
                                                                      pady=(10, 5))

        fields_frame = tk.Frame(tab)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 創建Treeview
        columns = ("磁場", "出現次數", "關鍵字")
        tree = ttk.Treeview(fields_frame, columns=columns, show="headings", height=6)

        # 設定列標題
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 填充數據
        for field, details in field_details.items():
            keywords = details.get("keywords", [])
            if isinstance(keywords, list):
                keywords = "、".join(keywords)

            tree.insert("", "end", values=(field, details.get("count", 0), keywords))

        # 添加滾動條
        scrollbar = tk.Scrollbar(fields_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.config(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)

        # 點選查看詳情功能
        tree.bind(
            "<Double-1>",
            lambda e: show_field_details_popup(tree.item(tree.focus())["values"][0], field_details))

        # 說明文字
        tk.Label(tab, text="雙擊磁場可查看詳細資訊", font=("Arial", 9), fg="gray").pack(anchor="w",
                                                                             padx=10,
                                                                             pady=(0, 10))
    else:
        tk.Label(tab, text="沒有可用的磁場詳細資訊", font=("Arial", 11)).pack(expand=True, pady=20)


def show_field_details(frame: tk.Frame, field_name, details):
    """顯示特定磁場的詳細資訊"""
    # 此方法需要被frame對象呼叫，用於更新顯示單個磁場的詳細信息
    for widget in frame.winfo_children():
        widget.destroy()

    # 返回按鈕
    back_btn = tk.Button(frame,
                         text="返回結果概覽",
                         command=lambda: frame.update_display(frame.last_result))
    back_btn.pack(anchor="w", padx=10, pady=10)

    # 磁場標題
    tk.Label(frame, text=f"{field_name} 磁場詳細資訊", font=("Arial", 14, "bold")).pack(anchor="w",
                                                                                  padx=10,
                                                                                  pady=(5, 15))

    # 關鍵字
    keywords = details.get("keywords", [])
    if isinstance(keywords, list):
        keywords = "、".join(keywords)

    tk.Label(frame, text="關鍵字:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(frame, text=keywords, wraplength=400).pack(anchor="w", padx=20, pady=(0, 10))

    # 優勢
    tk.Label(frame, text="優勢:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(frame, text=details.get("strengths", "無資料"), wraplength=400).pack(anchor="w",
                                                                               padx=20,
                                                                               pady=(0, 10))

    # 弱點
    tk.Label(frame, text="弱點:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(frame, text=details.get("weaknesses", "無資料"), wraplength=400).pack(anchor="w",
                                                                                padx=20,
                                                                                pady=(0, 10))

    # 財務建議
    tk.Label(frame, text="財務建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                   padx=10,
                                                                   pady=(10, 0))
    tk.Label(frame, text=details.get("financial_strategy", "無資料"),
             wraplength=400).pack(anchor="w", padx=20, pady=(0, 10))

    # 關係建議
    tk.Label(frame, text="關係建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                   padx=10,
                                                                   pady=(10, 0))
    tk.Label(frame, text=details.get("relationship_advice", "無資料"),
             wraplength=400).pack(anchor="w", padx=20, pady=(0, 10))


def show_lucky_numbers(frame, result_data: ResultData):
    """顯示幸運數字列表"""
    # 此方法需要被frame對象呼叫，用於單獨顯示幸運數字列表
    for widget in frame.winfo_children():
        widget.destroy()

    # 返回按鈕
    back_btn = tk.Button(frame,
                         text="返回結果概覽",
                         command=lambda: frame.update_display(frame.last_result))
    back_btn.pack(anchor="w", padx=10, pady=10)

    # 幸運數字標題
    tk.Label(frame, text="推薦幸運數字", font=("Arial", 14, "bold")).pack(anchor="w",
                                                                    padx=10,
                                                                    pady=(5, 15))

    recommendations = result_data.recommendations
    if not recommendations:
        tk.Label(frame, text="沒有可用的幸運數字推薦", font=("Arial", 12)).pack(expand=True)
        return

    # 使用Canvas和Frame組合實現可滾動區域
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 填充幸運數字
    for i, num in enumerate(recommendations, 1):
        num_frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=10, pady=10)
        num_frame.pack(fill="x", expand=True, padx=10, pady=5)

        tk.Label(num_frame, text=f"推薦 {i}", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(num_frame, text=num, font=("Courier", 14)).pack(anchor="w", pady=5)

        # 複製按鈕
        copy_btn = tk.Button(num_frame, text="複製", command=lambda n=num: copy_to_clipboard(n))
        copy_btn.pack(anchor="e")

    # 生成更多推薦數字的按鈕
    generate_btn = tk.Button(frame,
                             text="生成更多幸運數字",
                             command=lambda: generate_more_numbers_and_update(result_data))
    generate_btn.pack(pady=10)

    # 佈局滾動區域
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def show_field_details_popup(field_name, field_details):
    """在彈出窗口中顯示磁場詳細資訊"""
    if field_name not in field_details:
        messagebox.showinfo("提示", f"無法找到 {field_name} 的詳細資訊")
        return

    details = field_details[field_name]

    # 創建彈出窗口
    popup = tk.Toplevel()
    popup.title(f"{field_name} 磁場詳細資訊")
    popup.geometry("450x500")
    popup.resizable(False, False)

    # 關鍵字
    keywords = details.get("keywords", [])
    if isinstance(keywords, list):
        keywords = "、".join(keywords)

    tk.Label(popup, text="關鍵字:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 0))
    tk.Label(popup, text=keywords, wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

    # 優勢
    tk.Label(popup, text="優勢:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Label(popup, text=details.get("strengths", "無資料"), wraplength=400).pack(anchor="w",
                                                                               padx=30,
                                                                               pady=(0, 10))

    # 弱點
    tk.Label(popup, text="弱點:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Label(popup, text=details.get("weaknesses", "無資料"), wraplength=400).pack(anchor="w",
                                                                                padx=30,
                                                                                pady=(0, 10))

    # 財務建議
    tk.Label(popup, text="財務建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                   padx=20,
                                                                   pady=(10, 0))
    tk.Label(popup, text=details.get("financial_strategy", "無資料"),
             wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

    # 關係建議
    tk.Label(popup, text="關係建議:", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                   padx=20,
                                                                   pady=(10, 0))
    tk.Label(popup, text=details.get("relationship_advice", "無資料"),
             wraplength=400).pack(anchor="w", padx=30, pady=(0, 10))

    # 確認按鈕
    tk.Button(popup, text="確定", command=popup.destroy).pack(pady=20)


def show_number_detail(number_text):
    """顯示幸運數字詳細分析"""
    # 從列表項目文本中提取數字
    try:
        number = number_text.split(". ")[1]
    except:
        number = number_text

    # 創建彈出窗口
    popup = tk.Toplevel()
    popup.title(f"幸運數字詳情: {number}")
    popup.geometry("400x300")

    # 數字顯示
    tk.Label(popup, text=number, font=("Courier", 24, "bold")).pack(pady=(20, 10))

    # 數位分析
    tk.Label(popup, text="磁場分析", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

    digit_frame = tk.Frame(popup)
    digit_frame.pack(fill="x", padx=20, pady=5)

    # 分析幸運數字的磁場組合
    result = analyze_input(number)
    tk.Label(digit_frame, text=f"磁場組合：{result} ", anchor="w").pack(anchor="w")

    result_key = result.split()
    base_counts = Counter(result_key)
    for field, count in base_counts.items():
        keywords = "、".join(keyword_fields.get(field, []))  # 取得關鍵字集合並轉成字串
        tk.Label(digit_frame, text=f"{field}：{keywords} ", anchor="w").pack(anchor="w")

    # 這裡應該調用數字分析引擎的函數來分析數字，這裡只是簡單示例
    tk.Label(popup, text="此數字通常由有利的天醫、生氣和延年磁場組成", wraplength=350).pack(anchor="w", padx=30)

    # 複製按鈕
    tk.Button(popup, text="複製到剪貼簿", command=lambda: copy_to_clipboard(number)).pack(pady=15)


def copy_to_clipboard(text):
    """複製文本到剪貼簿"""
    try:
        # 清空剪貼簿
        root = tk._default_root
        root.clipboard_clear()

        # 設置新的剪貼簿內容
        root.clipboard_append(text)

        messagebox.showinfo("成功", "已複製到剪貼簿!")
    except Exception as e:
        logger.error(f"複製到剪貼簿失敗: {e}")
        messagebox.showerror("錯誤", f"複製失敗: {e}")


def save_result(result_data):
    """保存分析結果"""
    try:
        # 這裡應該調用result_controller的方法來保存結果
        from controller.result_controller import ResultController

        controller = ResultController()
        filepath = controller.save_to_history(result_data)

        if filepath:
            messagebox.showinfo("成功", f"已將分析結果保存到歷史記錄")
        else:
            messagebox.showwarning("警告", "保存失敗")
    except Exception as e:
        logger.error(f"保存結果失敗: {e}")
        messagebox.showerror("錯誤", f"保存失敗: {e}")


def export_report(result_data):
    """匯出分析報告"""
    try:
        # from tkinter import filedialog
        from controller.result_controller import ResultController

        # 選擇保存路徑
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("文本文件", "*.txt"), ("JSON文件", "*.json")],
                                                title="保存分析報告")

        if not filepath:
            return

        # 選擇格式
        format_type = "txt" if filepath.endswith(".txt") else "json"

        # 匯出報告
        controller = ResultController()
        if controller.export_result(filepath, format_type):
            messagebox.showinfo("成功", f"已匯出報告到 {filepath}")
        else:
            messagebox.showwarning("警告", "匯出失敗")
    except Exception as e:
        logger.error(f"匯出報告失敗: {e}")
        messagebox.showerror("錯誤", f"匯出失敗: {e}")


def show_visualization(result_data):
    """顯示磁場能量視覺化"""
    try:
        # 導入display_module來創建視覺化
        from ui.display_module import show_field_visualization

        # 創建彈出窗口
        popup = tk.Toplevel()
        popup.title("磁場能量視覺化")
        popup.geometry("600x500")

        # 調用視覺化函數
        show_field_visualization(popup, result_data)
    except Exception as e:
        logger.error(f"顯示視覺化失敗: {e}")
        messagebox.showerror("錯誤", f"無法顯示視覺化: {e}")


def generate_more_numbers_and_update(result_data: ResultData, update_callback=None):
    """生成更多推薦數字並更新數據和UI"""
    try:
        # 調用分析控制器來生成更多幸運數字
        from controller.analysis_controller import generate_lucky_numbers
        # from tkinter import simpledialog

        # 詢問要生成的數量
        count = simpledialog.askinteger("輸入",
                                        "請輸入要生成的幸運數字數量:",
                                        initialvalue=5,
                                        minvalue=1,
                                        maxvalue=20)

        if not count:
            return

        # 獲取當前的磁場計數
        adjusted_counts = result_data.adjusted_counts

        # 更新用_獲取當前的數字長度_從現有推薦數字推斷
        existing_recommendations = result_data.recommendations
        if existing_recommendations:
            digit_length = len(str(existing_recommendations[0]))
        else:
            digit_length = 4

        # 生成新的幸運數字
        new_numbers = generate_lucky_numbers(adjusted_counts, digit_length, count)

        if new_numbers:
            # 更新結果數據
            result_data.recommendations = new_numbers

            # 顯示更新成功
            messagebox.showinfo("成功", f"已生成 {len(new_numbers)} 個新的幸運數字")
    except Exception as e:
        logger.error(f"生成更多幸運數字失敗: {e}")
        messagebox.showerror("錯誤", f"生成失敗: {e}")
    return result_data


def make_result_view(root):

    # 創建結果框架
    result_frame = create_result_frame(root)
    result_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # 建立測試數據
    test_data = {
        "input_type": "姓名",
        "raw_analysis": "天醫 生氣 延年 五鬼 伏位 禍害 六煞 絕命",
        "counts": {
            "天醫": 1,
            "生氣": 1,
            "延年": 1,
            "五鬼": 1,
            "伏位": 1,
            "禍害": 1,
            "六煞": 1,
            "絕命": 1
        },
        "adjusted_counts": {
            "天醫": 1,
            "生氣": 1,
            "延年": 1,
            "伏位": 1
        },
        "adjust_log": ["(天醫-0)", "(絕命-1)", "(延年-0)", "(六煞-1)", "(生氣-0) (伏位-0) (禍害-1)", "(五鬼-1)"],
        "recommendations": ["1368", "3146", "6872", "1394", "6749"],
        "field_details": {
            "天醫": {
                "count": 1,
                "keywords": ["主大才", "天生聰穎", "文筆好"],
                "strengths": "賺錢有如神助、諸事順遂、外型氣質俱佳",
                "weaknesses": "極度善良，偶爾會被蒙騙",
                "financial_strategy": "智慧投資，行善積福，防範詐騙",
                "relationship_advice": "關懷對方，共同成長，給予情感支持"
            },
            "生氣": {
                "count": 1,
                "keywords": ["貴人", "轉機", "好名聲"],
                "strengths": "樂天派、凡事不強求、熱心助人、擁有好人緣",
                "weaknesses": "企圖心不旺盛，由於對任何事不強求隨遇而安",
                "financial_strategy": "積極開拓，慎選機遇，避免盲目跟風",
                "relationship_advice": "積極互動，珍惜緣分，避免過度追求新鮮感"
            },
            "延年": {
                "count": 1,
                "keywords": ["意志堅定的領袖格局"],
                "strengths": "決斷力強、內斂成熟",
                "weaknesses": "缺少彈性變通，做事強勢，一板一眼",
                "financial_strategy": "領導風範，規劃未來，長期財務規劃",
                "relationship_advice": "領導與支持，平衡關係，聆聽對方意見"
            },
            "伏位": {
                "count": 1,
                "keywords": ["蓄勢待發", "狀況延續", "臥虎藏龍"],
                "strengths": "有耐心、責任心強、幽默風趣、善於溝通協調",
                "weaknesses": "矛盾交錯、沒有安全感、主觀意識強、作風保守",
                "financial_strategy": "耐心積累，穩健投資，適合選擇風險較低、回報穩定的金融產品",
                "relationship_advice": "尋求穩定與安全感，在互動中需要耐心溝通"
            }
        },
        "digit_length": 4
    }

    # 測試按鈕
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    def load_test_data():
        result_frame.update_display(test_data)
        # 儲存最後的結果以便返回
        result_frame.last_result = test_data

    def show_field():
        if hasattr(result_frame, 'last_result'):
            field_name = tk.simpledialog.askstring("輸入", "請輸入要查看的磁場名稱:")
            if field_name and field_name in result_frame.last_result.get('field_details', {}):
                result_frame.show_field_details(
                    field_name, result_frame.last_result['field_details'][field_name])
            else:
                tk.messagebox.showwarning("警告", "找不到該磁場的詳細資訊")

    def show_numbers():
        if hasattr(result_frame, 'last_result'):
            result_frame.show_lucky_numbers(result_frame.last_result)

    tk.Button(button_frame, text="載入測試資料", command=load_test_data).pack(side="left", padx=5)
    tk.Button(button_frame, text="查看磁場詳情", command=show_field).pack(side="left", padx=5)
    tk.Button(button_frame, text="查看幸運數字", command=show_numbers).pack(side="left", padx=5)


# 測試代碼
if __name__ == "__main__":
    # 設定日誌級別
    logging.basicConfig(level=logging.DEBUG)

    # 創建測試窗口
    root = tk.Tk()
    root.title("結果顯示模組測試")
    root.geometry("800x600")

    # make_result_view(root)

    # 運行主循環
    root.mainloop()
