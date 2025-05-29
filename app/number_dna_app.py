#  app/number_dna_app.py
"""

數字DNA分析器 - 主應用程式類
管理應用程式生命週期與模組協調
初始化各個功能模組並協調它們之間的交互連接
提供所有程式設定和資源路徑

"""

import tkinter as tk
from tkinter import messagebox
import logging
import sys
import os
from pathlib import Path

# 導入配置和日誌工具
from utils.config import initialize as init_config, get_config, get_path
from utils.logging import initialize as init_logging, get_logger

# 導入資料層
from data import initialize as init_data
from data.rule_repository import RuleRepository
from data.file_manager import FileManager

# 導入核心層
from core.rule_parser import RuleParser
from core.field_analyzer import load_stroke_dict_from_file
from core.number_analyzer import magnetic_fields, keyword_fields
from core.recommendation_engine import generate_multiple_lucky_numbers

# 導入控制器層
from controller.input_controller import collect_input_data, validate_input
from controller.analysis_controller import analyze
from controller.result_controller import ResultController

# 導入UI層
from ui.main_window import main as ui_main
from ui.result_module import create_result_frame
from ui.input_module import create_input_frame
from ui.settings_module import create_settings_frame
from ui import init_ui_resources


class NumberDnaApp(tk.Tk):
    """數字DNA分析器主應用程式類"""

    def __init__(self, config_path=None):
        """初始化應用程式"""
        super().__init__()

        # 初始化日誌系統
        self.logger = get_logger("數字DNA分析器.App")
        self.logger.info("初始化主應用程式")

        # 設定基礎目錄
        self.base_dir = Path(__file__).parent.parent

        # 初始化配置管理器
        self.config_manager = init_config(config_path)

        # 初始化資料模組
        self._init_data_modules()

        # 初始化核心模組
        self._init_core_modules()

        # 初始化控制器模組
        self._init_controllers()

        # 初始化UI模組
        self._init_ui()

        # 綁定應用程式關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.logger.info("應用程式初始化完成")

    def _init_data_modules(self):
        """初始化數據相關模組"""
        self.logger.debug("初始化數據模組")

        try:
            # 初始化資料層
            self.file_manager, self.rule_repository = init_data(self.base_dir)

            # 驗證規則有效性
            is_valid, errors = self.rule_repository.validate_rules()
            if not is_valid:
                error_msg = "規則驗證失敗：\n" + "\n".join(errors)
                self.logger.warning(error_msg)
                # 在這裡不顯示錯誤訊息，等UI初始化後再顯示
                self.pending_error = error_msg
            else:
                self.pending_error = None

            # 載入規則
            self.rules = self.rule_repository.load_rules()

            self.logger.debug("數據模組初始化完成")
        except Exception as e:
            self.logger.error(f"數據模組初始化失敗: {e}", exc_info=True)
            raise RuntimeError(f"數據模組初始化失敗: {e}")

    def _init_core_modules(self):
        """初始化核心分析模組"""
        self.logger.debug("初始化核心模組")

        try:
            # 初始化規則解析器
            stroke_dict_path = get_path("stroke_dict_file")
            if not stroke_dict_path or not os.path.exists(stroke_dict_path):
                stroke_dict_path = os.path.join(self.base_dir, "resources", "characters.txt")

            self.logger.debug(f"筆劃字典路徑: {stroke_dict_path}")

            # 載入筆劃字典
            if os.path.exists(stroke_dict_path):
                self.stroke_dict = load_stroke_dict_from_file(stroke_dict_path)
                self.logger.debug(f"成功載入筆劃字典，共 {len(self.stroke_dict)} 個字元")
            else:
                self.logger.warning(f"筆劃字典檔案不存在: {stroke_dict_path}")
                self.stroke_dict = {}

            # 初始化規則解析器
            rules_dir = get_path("rule_dir")
            if not rules_dir:
                rules_dir = os.path.join(self.base_dir, "resources", "rules")

            self.rule_parser = RuleParser(rules_dir)
            self.logger.debug("規則解析器初始化完成")

            self.logger.debug("核心模組初始化完成")
        except Exception as e:
            self.logger.error(f"核心模組初始化失敗: {e}", exc_info=True)
            raise RuntimeError(f"核心模組初始化失敗: {e}")

    def _init_controllers(self):
        """初始化控制器模組"""
        self.logger.debug("初始化控制器模組")

        try:
            # 初始化結果控制器
            self.result_controller = ResultController()
            self.logger.debug("控制器模組初始化完成")
        except Exception as e:
            self.logger.error(f"控制器模組初始化失敗: {e}", exc_info=True)
            raise RuntimeError(f"控制器模組初始化失敗: {e}")

    def _init_ui(self):
        """初始化使用者介面"""
        self.logger.debug("初始化UI模組")

        try:
            # 設定UI資源路徑
            resources_dir = get_path("resources_dir")
            if not resources_dir:
                resources_dir = os.path.join(self.base_dir, "resources")

            init_ui_resources(resources_dir)

            # 設定應用程式屬性
            self.title("數字DNA分析器")
            width = get_config("app", "window_width", 1000)
            height = get_config("app", "window_height", 600)
            self.geometry(f"{width}x{height}")
            self.minsize(800, 500)

            # 設定背景顏色
            bg_color = get_config("ui", "color_scheme", {}).get("background", "#fefae0")
            self.config(bg=bg_color)

            # 創建主視窗內容框架
            self.main_frame = tk.Frame(self, bg=bg_color)
            self.main_frame.pack(fill="both", expand=True)

            # ===== 標題區 =====
            header_font_size = get_config("ui", "header_font_size", 24)
            header_color = get_config("ui", "color_scheme", {}).get("header", "#283618")

            title_label = tk.Label(self.main_frame,
                                   text="數字DNA分析器",
                                   font=("Arial", header_font_size, "bold"),
                                   bg=bg_color,
                                   fg=header_color)
            title_label.pack(pady=10)

            # ===== 內容主框架 =====
            content_frame = tk.Frame(self.main_frame, bg=bg_color)
            content_frame.pack(fill="both", expand=True, padx=20)

            # 左邊：輸入框區域
            left_frame = tk.Frame(content_frame, bg=bg_color)
            left_frame.pack(side="left", fill="y", padx=10)

            # 右邊：結果顯示區域
            self.result_frame = create_result_frame(content_frame)
            self.result_frame.pack(side="left", expand=True, fill="both", padx=10)

            # 儲存結果框架的引用，供控制器使用
            self.result_controller.result_frame = self.result_frame

            # 創建輸入模組
            self.input_frame = create_input_frame(left_frame, self.result_frame)
            self.input_frame.pack(pady=10, fill="x")

            self.logger.debug("UI模組初始化完成")

            # 如果有待顯示的錯誤訊息，顯示它
            if hasattr(self, 'pending_error') and self.pending_error:
                self.after(1000, lambda: messagebox.showwarning("規則驗證警告", self.pending_error))

        except Exception as e:
            self.logger.error(f"UI模組初始化失敗: {e}", exc_info=True)
            raise RuntimeError(f"UI模組初始化失敗: {e}")

    def run(self):
        """啟動應用程式主迴圈"""
        self.logger.info("啟動應用程式主迴圈")

        # 顯示應用程式啟動提示
        self.after(500, lambda: messagebox.showinfo("歡迎", "歡迎使用數字DNA分析器！\n請輸入資料並選擇分析條件以開始。"))

        # 啟動主循環
        self.mainloop()

    def _on_closing(self):
        """應用程式關閉處理"""
        self.logger.info("應用程式準備關閉")

        # 儲存任何未保存的資料
        try:
            # 儲存配置
            from utils.config import save_config
            save_config()

            self.logger.debug("已保存配置")
        except Exception as e:
            self.logger.error(f"保存配置失敗: {e}")

        # 關閉應用程式
        self.destroy()
        self.logger.info("應用程式已關閉")

    def show_about(self):
        """顯示關於對話框"""
        about_text = """數字DNA分析器 v1.0.0

一款基於易經數字能量分析的應用程式，
可以分析姓名、生日、身分證等數據中的磁場能量，
並提供幸運數字建議。

Copyright © 2025 All Rights Reserved
"""
        messagebox.showinfo("關於數字DNA分析器", about_text)

    def show_help(self):
        """顯示幫助對話框"""
        help_text = """使用說明：

1. 輸入區：選擇並輸入姓名、身分證或自定義資料
2. 設定區：選擇數字位數、英數混合選項等
3. 分析按鈕：點擊後進行分析並顯示結果
4. 結果區：查看分析結果、幸運數字和磁場詳情

更多幫助請參考說明文件。
"""
        messagebox.showinfo("使用說明", help_text)

    def reset_rules(self):
        """重置規則為預設值"""
        if messagebox.askyesno("確認", "確定要重置所有規則為預設值嗎？此操作無法復原。"):
            try:
                # 備份當前規則
                success, backup_dir = self.rule_repository.backup_rules()
                if success:
                    self.logger.info(f"已備份當前規則到 {backup_dir}")

                # 重置規則
                if self.rule_repository.reset_to_default():
                    self.logger.info("已重置規則為預設值")
                    messagebox.showinfo("成功", "已重置規則為預設值。\n請重新啟動應用程式以套用變更。")
                else:
                    messagebox.showerror("錯誤", "重置規則失敗。")
            except Exception as e:
                self.logger.error(f"重置規則失敗: {e}")
                messagebox.showerror("錯誤", f"重置規則失敗: {e}")


# 如果直接執行此模組，創建並啟動應用程式
if __name__ == "__main__":
    # 初始化日誌系統
    init_logging(level=logging.DEBUG)

    try:
        # 創建應用程式實例
        app = NumberDnaApp()

        # 啟動應用程式
        app.run()
    except Exception as e:
        logging.critical(f"應用程式啟動失敗: {e}", exc_info=True)
        messagebox.showerror("嚴重錯誤", f"應用程式啟動失敗:\n{e}")
        sys.exit(1)
