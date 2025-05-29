#  core/__init__.py
"""
數字DNA分析器 - 核心分析模組
提供數字能量分析、磁場計算和幸運數字推薦功能的核心實現
"""

# 核心功能
from core.field_analyzer import (
    analyze_input,
    analyze_name_strokes,
    analyze_mixed_input,
    load_stroke_dict_from_file
)

from core.number_analyzer import (
    magnetic_fields,
    keyword_fields
)

from core.recommendation_engine import (
    generate_multiple_lucky_numbers,
    generate_lucky_number_chain_by_cancel_fields
)

from core.rule_parser import RuleParser

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = [
    # 從field_analyzer導出
    'analyze_input',
    'analyze_name_strokes',
    'analyze_mixed_input',
    'load_stroke_dict_from_file',

    # 從number_analyzer導出
    'magnetic_fields',
    'keyword_fields',

    # 從recommendation_engine導出
    'generate_multiple_lucky_numbers',
    'generate_lucky_number_chain_by_cancel_fields',

    # 從rule_parser導出
    'RuleParser'
]