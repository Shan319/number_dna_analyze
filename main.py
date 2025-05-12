#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
數字DNA分析器 - 主程式入口點
提供數字能量分析與幸運數字推薦功能
"""

import sys
import logging
from pathlib import Path
import tkinter as tk

# 設定資源路徑
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / "logs" / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("數字DNA分析器")

# 匯入主應用程式
try:
    from app.number_dna_app import DigitalDnaApp
    from utils.config import ConfigManager
except ImportError as e:
    logger.critical(f"匯入模組失敗: {e}")
    print(f"錯誤: 無法載入必要模組，請確認安裝所有依賴項: {e}")
    sys.exit(1)


def main():
    """主程式入口函數"""
    logger.info("啟動數字DNA分析器應用程式")

    try:
        # 建立目錄確保存在
        (BASE_DIR / "logs").mkdir(exist_ok=True)
        (BASE_DIR / "data").mkdir(exist_ok=True)
        (BASE_DIR / "data" / "history").mkdir(exist_ok=True)

        # 載入設定
        config_manager = ConfigManager(BASE_DIR / "config.yaml")

        # 初始化應用程式
        app = DigitalDnaApp(config_manager)

        # 設定應用程式屬性
        app.title("數字DNA分析器")
        app.geometry("900x600")
        app.minsize(800, 500)

        # 啟動應用程式
        logger.info("進入主循環")
        app.mainloop()
        logger.info("程式結束")

    except Exception as e:
        logger.critical(f"程式啟動錯誤: {e}", exc_info=True)
        print(f"程式發生嚴重錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()