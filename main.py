# main.py
"""
數字DNA分析器 - 主程式入口點
提供數字能量分析與幸運數字推薦功能
"""

import os
import sys
import logging
from pathlib import Path
from tkinter import messagebox

# 載入 UI 主畫面
from ui.main_window import MainView
# 執行 pip 升級與安裝套件
# upgrade_pip()
# ensure_requirements()

# 設定目錄與資源位置
BASE_DIR = Path(__file__).resolve().parent
log_dir = BASE_DIR / "logs"
history_dir = BASE_DIR / "data" / "history"
resources_dir = BASE_DIR / "resources"

for path in [log_dir, history_dir, resources_dir / "rules", resources_dir / "images"]:
    path.mkdir(parents=True, exist_ok=True)

# 日誌設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s (%(name)s)[%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
              logging.StreamHandler()])

logger = logging.getLogger("數字DNA分析器")


# 檢查必備檔案
def check_required_files():
    required_files = [
        resources_dir / "characters.txt", resources_dir / "rules" / "base_rules.json",
        resources_dir / "rules" / "field_rules.json"
    ]
    for file_path in required_files:
        if not file_path.exists():
            logger.warning(f"缺少必要檔案: {file_path}")
            return False
    return True


# 未捕捉例外處理
def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error("未捕獲的異常", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror("錯誤", f"發生意外錯誤: {exc_value}\n\n請聯繫開發人員。")


sys.excepthook = handle_exception


# 主程式進入點
def main():
    logger.info("啟動數字DNA分析器")
    if not check_required_files():
        messagebox.showerror("初始化失敗", "缺少必要的資源檔案。請確認 resources 資料夾下的檔案齊全。")
        sys.exit(1)

    mainview = MainView()
    mainview.mainloop()


if __name__ == "__main__":
    main()
