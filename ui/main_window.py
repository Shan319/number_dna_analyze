# ui/main_window.py
import tkinter as tk

from data.result_data import ResultData
from ui.input_module import InputView
from ui.history_module import HistoryView
from ui.result_module import ResultView


class MainView:
    """主畫面
    """

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("數字DNA分析器")
        self.root.geometry("1000x700")
        self.root.config(bg="#fefae0")

        # ===== 標題區 =====
        title_label = tk.Label(self.root, text="數字DNA分析器", font=("Arial", 24, "bold"), bg="#fefae0")
        title_label.pack(pady=10)

        # ===== 內容主框架 =====
        content_frame = tk.Frame(self.root, bg="#fefae0")
        content_frame.pack(fill="both", expand=True, padx=20)

        # 左邊
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # 左邊：輸入區域
        self.input_frame = InputView(left_frame)
        self.input_frame.frame.pack(padx=10, pady=10, fill="x")

        # 左邊：歷史紀錄區域
        self.history_view = HistoryView(left_frame)
        self.history_view.frame.pack(padx=10, pady=10, fill="x")

        # 右邊
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # 右邊：結果顯示區域
        self.result_view = ResultView(right_frame)
        self.result_view.frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Hook notifications.
        self.input_frame.notify_update_history_view = self.notify_update_history_view
        self.input_frame.notify_update_result_view = self.notify_update_result_view
        self.history_view.notify_update_result_view = self.notify_update_result_view

    def notify_update_result_view(self, result_data: ResultData | None = None):
        self.result_view.result_data = result_data
        self.result_view.update_display()

    def notify_update_history_view(self):
        self.history_view.update_display()

    def notify_update_input_view(self, result_data: ResultData | None = None):
        self.result_view.result_data = result_data
        self.result_view.update_display()

    def mainloop(self):
        self.root.mainloop()


if __name__ == "__main__":
    main = MainView()
    main.mainloop()
