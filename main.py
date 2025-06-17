# main.py
"""
數字 DNA 分析器 - 主程式入口點
提供數字能量分析與幸運數字推薦功能
"""

import sys
from tkinter import messagebox

from src.config.main_config import get_main_config

from src.utils.file_manager import FileManager
from src.utils.cryptography import AESEncryptionFernet
from src.utils.log_provider.log_provider_interface import Level
from src.utils.log_provider.log_provider_real_impl import LogProviderRealImpl
from src.utils import main_service
from src.ui.main_window import MainView


# 主程式進入點
def main():
    main_config = get_main_config()
    log_level = Level[main_config.log_level]

    # Prepare Providers - File Manager
    file_manager = FileManager()
    main_service.file_manager = file_manager

    # Prepare Providers - Log
    main_service.log = LogProviderRealImpl(file_manager.log_dir, None, "數字 DNA 分析器")
    main_service.log.set_level(main_config.log_level)
    logger = main_service.log.get_logger()
    logger.info("啟動數字 DNA 分析器")

    # Prepare Providers - Cryptography
    cryptography = AESEncryptionFernet(file_manager)
    main_service.cryptography = cryptography

    # 未捕捉例外處理
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("未捕獲的異常", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror("錯誤", f"發生意外錯誤: {exc_value}\n\n請聯繫開發人員。")

    sys.excepthook = handle_exception

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
