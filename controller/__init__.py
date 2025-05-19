#  controller/__init__.py
"""
數字DNA分析器 - 控制器模組
連接核心分析功能和用戶界面之間
"""

# 導入控制器模組中的關鍵類和函數
from controller.input_controller import collect_input_data, validate_input, prepare_input_for_analysis
from controller.analysis_controller import analyze
from controller.result_controller import ResultController

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = [
    'collect_input_data',  # 從input_controller導出
    'validate_input',      # 從input_controller導出
    'prepare_input_for_analysis',  # 從input_controller導出
    'analyze',             # 從analysis_controller導出
    'ResultController'     # 從result_controller導出
]