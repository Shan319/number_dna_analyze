# ui/main_window.py
import tkinter as tk
from ui.input_module import create_input_frame
from ui.history_module import HistoryView
from ui.result_module import create_result_content


def main():
    root = tk.Tk()
    root.title("數字DNA分析器")
    root.geometry("1000x700")
    root.config(bg="#fefae0")

    # ===== 標題區 =====
    title_label = tk.Label(root, text="數字DNA分析器", font=("Arial", 24, "bold"), bg="#fefae0")
    title_label.pack(pady=10)

    # ===== 內容主框架 =====
    content_frame = tk.Frame(root, bg="#fefae0")
    content_frame.pack(fill="both", expand=True, padx=20)

    # 左邊：輸入框區域
    left_frame = tk.Frame(content_frame)
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    # 右邊：結果顯示區域
    right_frame = tk.Frame(content_frame)
    right_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    result_frame = create_result_content(right_frame, None)
    result_frame.pack(expand=True, fill="both", padx=10, pady=10)

    # 歷史紀錄區域
    history_view = HistoryView(left_frame, right_frame)
    history_frame = history_view.frame

    # 傳 result_frame 給輸入模組（用於顯示分析結果）
    input_frame = create_input_frame(left_frame, right_frame, history_view.update_history_data)
    input_frame.pack(padx=10, pady=10, fill="x")

    history_frame.pack(padx=10, pady=10, fill="x")

    root.mainloop()


if __name__ == "__main__":
    main()
