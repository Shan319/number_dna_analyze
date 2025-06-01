#  controller/input_controller.py

import logging

import tkinter as tk

# from ui.settings_module import (digit_var, custom_digit_var, mixed_var, english_position_var,
#                                 fixed_num_var, default_vars, other_vars)
#  from core.number_analyzer import analyze_number
#  from utils.validators import is_valid_id, is_valid_digit_length, is_valid_fixed_num

from utils.validators import validate_all
from data.input_data import InputData, InputType, FixDigitsPosition
# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.InputController")


def collect_input_data(
    name_var: tk.StringVar,
    id_var: tk.StringVar,
    phone_var: tk.StringVar,
    birth_var: tk.StringVar,
    custom_var: tk.StringVar,
    use_name: tk.BooleanVar,
    use_id: tk.BooleanVar,
    use_phone: tk.BooleanVar,
    use_birth: tk.BooleanVar,
    use_custom: tk.BooleanVar,
    digit_var: tk.StringVar,
    custom_digit_var: tk.StringVar,
    mixed_var: tk.BooleanVar,
    english_position_var: tk.StringVar,
    fixed_num_var: tk.StringVar,
    default_vars: dict[str, tk.BooleanVar],
    other_vars: dict[str, tk.BooleanVar],
):
    """
    從UI元素中收集輸入數據
    """
    logger.debug("開始收集用戶輸入資料")

    # 讀取輸入及輸入類型
    input_type = InputType.NONE
    input_value = ""
    if use_name.get():
        input_type = InputType.NAME
        input_value = name_var.get()
    elif use_id.get():
        input_type = InputType.ID
        input_value = id_var.get()
    elif use_phone.get():
        input_type = InputType.PHONE
        input_value = phone_var.get()
    elif use_birth.get():
        input_type = InputType.BIRTH
        input_value = birth_var.get()
    elif use_custom.get():
        input_type = InputType.CUSTOM
        input_value = custom_var.get()

    input_value = input_value.strip()

    # 讀取數字位數限制
    digit_value = digit_var.get()
    if digit_value == "custom":
        digits = (custom_digit_var.get().strip())
    else:
        digits = (digit_value)

    # 讀取固定英數字
    custom_digits_length = mixed_var.get()
    english_position = english_position_var.get()
    fixed_digits_position = FixDigitsPosition.NONE
    fixed_digits_value: str = ""
    if custom_digits_length:
        if english_position == "前":
            fixed_digits_position = FixDigitsPosition.BEGIN
        elif english_position == "中":
            fixed_digits_position = FixDigitsPosition.CENTER
        elif english_position == "後":
            fixed_digits_position = FixDigitsPosition.END
        fixed_digits_value = fixed_num_var.get().strip()

    default_conditions: dict[str, bool] = {}
    other_conditions: dict[str, bool] = {}

    for k, v in default_vars.items():
        default_conditions[k] = v.get()

    for k, v in other_vars.items():
        other_conditions[k] = v.get()

    input_data = InputData(input_type=input_type,
                           input_value=input_value,
                           digits_length=digits,
                           custom_digits_length=custom_digits_length,
                           fixed_digits_position=fixed_digits_position,
                           fixed_digits_value=fixed_digits_value,
                           default_conditions=default_conditions,
                           other_conditions=other_conditions)
    return input_data


# def collect_input_data(name_var, id_var, custom_var, use_name, use_id, use_custom):
#     logger.debug("開始收集用戶輸入資料")
#     input_data = {}

#     if use_name.get():
#         input_data["name"] = name_var.get().strip()
#     if use_id.get():
#         input_data["id"] = id_var.get().strip()
#     if use_custom.get():
#         input_data["custom"] = custom_var.get().strip()

#     # 讀取數字位數限制
#     digit_value = digit_var.get()
#     input_data["digit_length"] = (
#         custom_digit_var.get().strip() if digit_value == "custom" else digit_value
#     )

#     # 讀取英數混合模式設定
#     input_data["mix_mode"] = mixed_var.get()
#     input_data["english_position"] = english_position_var.get()
#     input_data["fixed_num"] = fixed_num_var.get().strip()
#     input_data["default_conditions"] = {k: v.get() for k, v in default_vars.items()}
#     input_data["other_conditions"] = {k: v.get() for k, v in other_vars.items()}


#     return input_data
def validate_input(input_data):
    """
    驗證輸入數據的有效性

    Args:
        input_data (dict): 收集的輸入資料字典

    Returns:
        tuple: (是否有效, 錯誤訊息列表)
    """
    # 添加其他檢查
    errors = []

    # 檢查是否有至少一個輸入
    if not any(key in input_data for key in ["name", "id", "phone", "birth", "custom"]):
        errors.append("請至少選擇一種輸入類型（姓名、身分證、手機、生日、英數混合）")

    # 使用validate_all添加其他常規檢查
    errors.extend(validate_all(input_data))

    # 添加混合模式的檢查
    if input_data.get("mix_mode", False) and not input_data.get("fixed_eng"):
        if input_data.get("english_position") not in ["前", "中", "後"]:
            errors.append("使用英數混合模式時，必須指定英文位置或提供固定英文")

    return (len(errors) == 0, errors)


def prepare_input_for_analysis(input_data):
    """
    將收集到的輸入資料處理成可以分析的格式

    Args:
        input_data (dict): 收集到的輸入資料

    Returns:
        dict: 準備好可以分析的資料
    """
    prepared_data = input_data.copy()

    # 添加輸入類型標記
    if "name" in input_data and input_data["name"]:
        prepared_data["input_type"] = "name"
    elif "id" in input_data and input_data["id"]:
        prepared_data["input_type"] = "id"
    elif "custom" in input_data and input_data["custom"]:
        prepared_data["input_type"] = "custom"

    # 處理數字長度設定
    if input_data.get("digit_length") == "custom":
        try:
            prepared_data["actual_digit_length"] = int(input_data.get("custom_digit", "8"))
        except ValueError:
            prepared_data["actual_digit_length"] = 8
            logger.warning("自定義位數格式錯誤，使用預設值8")
    else:
        try:
            prepared_data["actual_digit_length"] = int(input_data.get("digit_length", "8"))
        except ValueError:
            prepared_data["actual_digit_length"] = 8
            logger.warning("數字位數格式錯誤，使用預設值8")

    # 處理選中的條件
    selected_conditions = []

    # 添加默認條件
    for key, value in input_data.get("default_conditions", {}).items():
        if value:
            selected_conditions.append(key)

    # 添加其他條件
    for key, value in input_data.get("other_conditions", {}).items():
        if value:
            selected_conditions.append(key)

    prepared_data["selected_conditions"] = selected_conditions

    logger.debug(f"已準備分析數據: {prepared_data}")
    return prepared_data


def save_input_history(input_data: InputData, file_manager):
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
                "custom_digit": input_data.custom_digits_length,
                "mix_mode": input_data.fixed_digits_position == FixDigitsPosition.NONE,
                "english_position": input_data.fixed_digits_position.value,
                "fixed_num": input_data.fixed_digits_value,
                "default_conditions": input_data.default_conditions,
                "other_conditions": input_data.other_conditions
            }
        }

        # 使用文件管理器保存
        if hasattr(file_manager, "save_history"):
            file_path = file_manager.save_history(input_type, history_data)
            logger.info(f"已保存 {input_type} 輸入歷史: {value}, 路徑: {file_path}")
            return True
        else:
            logger.error("文件管理器缺少save_history方法")
            return False

    except Exception as e:
        logger.error(f"保存輸入歷史失敗: {e}", exc_info=True)
        return False
