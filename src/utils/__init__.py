#  utils/__init__.py
"""
數字 DNA 分析器 - 通用工具模組包
提供跨模組共用的工具函數和設施

此模組包含：
1. 配置管理（config）
2. 日誌工具（logging）
3. 資料驗證（validators）
"""
from .file_manager import FileManager
from .cryptography import AESEncryptionFernet
from .log_provider.log_provider_interface import LogProviderInterface


class MainService:

    def __init__(self) -> None:
        self.file_manager: FileManager
        self.cryptography: AESEncryptionFernet
        self.log: LogProviderInterface


main_service = MainService()
