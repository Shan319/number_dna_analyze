# main.py
"""
數字DNA分析器 - 主程式入口點
提供數字能量分析與幸運數字推薦功能
"""

import os
import sys
import logging
from pathlib import Path
import tkinter as tk
from ui.main_window import main as ui_main

# 設定資源路徑
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 建立目錄儲存使用者結果
log_dir = os.path.join(BASE_DIR, "logs")
history_dir = os.path.join(BASE_DIR, "data", "history")
os.makedirs(log_dir, exist_ok=True)
os.makedirs(history_dir, exist_ok=True)

# 確保resources目錄也存在
resources_dir = os.path.join(BASE_DIR, "resources")
os.makedirs(resources_dir, exist_ok=True)
os.makedirs(os.path.join(resources_dir, "rules"), exist_ok=True)
os.makedirs(os.path.join(resources_dir, "images"), exist_ok=True)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s (%(name)s)[%(levelname)s] %(message)s',
    # handlers=[
    #     logging.FileHandler(BASE_DIR / "logs" / "app.log", encoding="utf-8"),
    #     logging.StreamHandler()
    # ]
    handlers=[
        logging.FileHandler(os.path.join("logs", "app.log"), encoding="utf-8"),
        logging.StreamHandler()
    ])

logger = logging.getLogger("數字DNA分析器")

# # 匯入主應用程式
# try:
#     from app.number_dna_app import DigitalDnaApp
#     # from utils.config import ConfigManager
# except ImportError as e:
#     logger.critical(f"匯入模組失敗: {e}")
#     print(f"錯誤: 無法載入必要模組，請確認安裝所有依賴項: {e}")
#     sys.exit(1)


def main():
    """主程式入口函數"""
    logger.info("啟動數字DNA分析器應用程式")

    # 檢查必要的檔案是否存在
    if not check_required_files():
        logger.error("缺少必要的資源檔案，程式無法正常運行")
        print("初始化失敗：缺少必要的資源檔案。請確保resources目錄中包含必要的規則檔案和字元對照表。")
        sys.exit(1)

    try:
        ui_main()
        # (BASE_DIR / "logs").mkdir(exist_ok=True)
        # (BASE_DIR / "data").mkdir(exist_ok=True)
        # (BASE_DIR / "data" / "history").mkdir(exist_ok=True)
    except Exception as e:
        logger.critical(f"程式啟動錯誤: {e}", exc_info=True)
        print(f"程式發生嚴重錯誤: {e}")
        sys.exit(1)


def check_required_files():
    """檢查必要的資源檔案是否存在"""
    required_files = [
        os.path.join(BASE_DIR, "resources", "characters.txt"),
        os.path.join(BASE_DIR, "resources", "rules", "base_rules.json"),
        os.path.join(BASE_DIR, "resources", "rules", "field_rules.json")
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.warning(f"缺少必要檔案: {file_path}")
            return False

    return True

def handle_exception(exc_type, exc_value, exc_traceback):
    """處理異常函數"""
    logger.error("未捕獲的異常", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror("錯誤", f"發生意外錯誤: {exc_value}\n\n請聯繫開發人員。")

sys.excepthook = handle_exception

if __name__ == "__main__":
    main()
