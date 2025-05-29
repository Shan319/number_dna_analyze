#  ui/__init__.py
"""
數字DNA分析器 - 使用者介面模組包
提供GUI元件和視覺化展示功能

此模組包含：
1. 主視窗管理（main_window）
2. 輸入介面（input_module）
3. 設定界面（settings_module）
4. 結果展示（result_module）
5. 視覺化顯示（display_module）
"""

# 導入UI模組組件
from ui.main_window import main
from ui.input_module import create_input_frame
from ui.settings_module import (create_settings_frame, digit_var, custom_digit_var, mixed_var,
                                english_position_var, fixed_num_var, default_vars, other_vars)
# from ui.result_module import create_result_frame

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = [
    # 主視窗
    'main',

    # 輸入介面
    'create_input_frame',

    # 設定介面
    'create_settings_frame',
    'digit_var',
    'custom_digit_var',
    'mixed_var',
    'english_position_var',
    'fixed_num_var',
    'default_vars',
    'other_vars',

    # # 結果展示
    # 'create_result_frame'
]


# 註冊資源路徑
def init_ui_resources(resource_path=None):
    """
    初始化UI資源

    Args:
        resource_path: 資源目錄路徑，如果為None則使用默認路徑
    """
    import os
    from pathlib import Path
    import logging

    logger = logging.getLogger("數字DNA分析器.UI")

    if resource_path is None:
        # 默認資源路徑
        base_dir = Path(__file__).parent.parent
        resource_path = os.path.join(base_dir, "resources")

    if os.path.exists(resource_path):
        logger.info(f"UI資源路徑設定為: {resource_path}")
    else:
        logger.warning(f"UI資源路徑不存在: {resource_path}")
