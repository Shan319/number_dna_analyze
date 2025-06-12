#  controller/input_controller.py

import logging

import tkinter as tk

from utils.validators import validate_all
from data.input_data import InputData, InputType, FixDigitsPosition
from data.file_manager import FileManager

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.InputController")


def save_input_history(input_data: InputData, file_manager: FileManager):
    """
    保存輸入歷史

    Args:
        input_data (InputData): 輸入數據
        file_manager: 文件管理器

    Returns:
        bool: 是否成功保存
    """
    try:
        # 確定輸入類型
        input_type = input_data.input_type.value
        value = input_data.input_value

        # 準備要保存的歷史記錄數據
        history_data = {
            "value": value,
            "timestamp": None,  # file_manager.save_history會自動添加時間戳
            "settings": {
                "digit_length": input_data.digits_length,
                "custom_digit": input_data.is_custom_digits_length,
                "mix_mode": input_data.fixed_digits_position == FixDigitsPosition.NONE,
                "english_position": input_data.fixed_digits_position.value,
                "fixed_num": input_data.fixed_digits_value,
                "default_conditions": input_data.default_conditions,
                "other_conditions": input_data.other_conditions
            }
        }

        # 使用文件管理器保存
        file_path = file_manager.save_history(input_type, history_data)
        logger.info(f"已保存 {input_type} 輸入歷史: {value}, 路徑: {file_path}")
        return True

    except Exception as e:
        logger.error(f"保存輸入歷史失敗: {e}", exc_info=True)
        return False
