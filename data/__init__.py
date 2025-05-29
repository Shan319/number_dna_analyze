#  data/__init__.py
"""
數字DNA分析器 - 資料層模組包
管理應用程式的資料存取、模型和規則

此模組包含：
1. 資料模型定義 (models)
2. 檔案管理功能 (file_manager)
3. 資料加密服務 (encryption)
4. 規則儲存庫 (rule_repository)
"""

# 導入核心功能
from data.models import (
    MagneticField, InputData, AnalysisResult,
    MagneticPair, RuleModel, UserProfile,
    convert_to_model, convert_to_dict, validate_model
)

from data.file_manager import FileManager

# 條件導入加密功能
try:
    from data.encryption import (
        encrypt_data, decrypt_data, encrypt_json, decrypt_json,
        is_encrypted, encrypt_file, decrypt_file, initialize as init_encryption
    )
    encryption_available = True
except ImportError:
    encryption_available = False

from data.rule_repository import RuleRepository

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = [
    # 資料模型
    'MagneticField', 'InputData', 'AnalysisResult',
    'MagneticPair', 'RuleModel', 'UserProfile',
    'convert_to_model', 'convert_to_dict', 'validate_model',

    # 檔案管理
    'FileManager',

    # 規則儲存庫
    'RuleRepository',

    # 加密服務 (如果可用)
    'encrypt_data', 'decrypt_data', 'encrypt_json', 'decrypt_json',
    'is_encrypted', 'encrypt_file', 'decrypt_file', 'init_encryption'
]

# 加密可用性
__all__.append('encryption_available')

# 初始化函數
def initialize(base_dir=None, enable_encryption=True):
    """
    初始化資料層

    Args:
        base_dir: 基礎目錄路徑
        enable_encryption: 是否啟用加密

    Returns:
        tuple: (file_manager, rule_repository)
    """
    # 初始化檔案管理器
    file_manager = FileManager(base_dir=base_dir, enable_encryption=enable_encryption and encryption_available)

    # 初始化規則儲存庫
    rule_repository = RuleRepository(file_manager=file_manager)

    # 如果加密可用且啟用，初始化加密服務
    if encryption_available and enable_encryption:
        init_encryption()

    return file_manager, rule_repository