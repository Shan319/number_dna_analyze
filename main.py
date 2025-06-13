# main.py
"""
數字DNA分析器 - 主程式入口點
提供數字能量分析與幸運數字推薦功能
"""

import sys
import logging
from tkinter import messagebox

from src.data.file_manager import file_manager
from src.ui.main_window import MainView


# 主程式進入點
def main():
    file_manager.ensure_required_dirs()
    log_path = file_manager.get_log_path()

    # 日誌設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s (%(name)s)[%(levelname)s] %(message)s',
        handlers=[logging.FileHandler(log_path, encoding="utf-8"),
                  logging.StreamHandler()])

    logger = logging.getLogger("數字DNA分析器")

    # 未捕捉例外處理
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("未捕獲的異常", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror("錯誤", f"發生意外錯誤: {exc_value}\n\n請聯繫開發人員。")

    sys.excepthook = handle_exception

    logger.info("啟動數字DNA分析器")
    required_files = file_manager.check_required_files()
    for path, exist in required_files.items():
        if exist:
            continue
        logger.error(f"缺少必要檔案: {path}")
    if not all(required_files.values()):
        messagebox.showerror("初始化失敗", "缺少必要的資源檔案。請確認 resources 資料夾下的檔案齊全。")
        sys.exit(1)

    mainview = MainView()
    mainview.mainloop()


if __name__ == "__main__":
    main()
