#  utils/__init__.py
"""
數字DNA分析器 - 通用工具模組包
提供跨模組共用的工具函數和設施

此模組包含：
1. 配置管理（config）
2. 日誌工具（logging）
3. 資料驗證（validators）
"""

# 導入核心功能
from utils.config import (
    initialize as init_config,
    get_config, set_config, save_config,
    get_path, is_feature_enabled
)

from utils.logging import (
    initialize as init_logging,
    get_logger, set_level,
    DEBUG, INFO, WARNING, ERROR, CRITICAL,
    log_function_call, log_class_methods
)

from utils.validators import (
    is_valid_id, is_valid_digit_length,
    is_valid_fixed_eng, is_valid_fixed_num,
    validate_all
)

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = [
    # 配置管理
    'init_config',
    'get_config', 'set_config', 'save_config',
    'get_path', 'is_feature_enabled',

    # 日誌工具
    'init_logging',
    'get_logger', 'set_level',
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
    'log_function_call', 'log_class_methods',

    # 驗證工具
    'is_valid_id', 'is_valid_digit_length',
    'is_valid_fixed_eng', 'is_valid_fixed_num',
    'validate_all'
]

# 初始化工具模組
def initialize(config_path=None, log_path=None, log_level=INFO):
    """
    初始化工具模組

    Args:
        config_path: 配置文件路徑，如果為None則使用默認路徑
        log_path: 日誌文件目錄，如果為None則使用默認路徑
        log_level: 日誌級別，默認為INFO

    Returns:
        (config_manager, logger_manager): 配置管理器和日誌管理器的元組
    """
    # 初始化配置管理器
    config_manager = init_config(config_path)

    # 如果未提供日誌路徑，但有配置，則從配置獲取
    if log_path is None and config_manager is not None:
        log_path = get_path("logs_dir")

    # 初始化日誌管理器
    logger_manager = init_logging(log_path, log_level)

    return config_manager, logger_manager
