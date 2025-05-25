#  controller/input_controller.py

import logging
from ui.settings_module import (
    digit_var, custom_digit_var,
    mixed_var, english_position_var,
    fixed_eng_var, fixed_num_var,
    default_vars, other_vars
)
#  from core.number_analyzer import analyze_number
#  from utils.validators import is_valid_id, is_valid_digit_length, is_valid_fixed_eng, is_valid_fixed_num
from utils.validators import validate_all

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.InputController")

def collect_input_data(name_var, id_var, phone_var, birth_var,custom_var, use_name, use_id,use_phone,use_birth, use_custom,
                       digit_var=None, custom_digit_var=None, mixed_var=None,
                       english_position_var=None, fixed_eng_var=None, fixed_num_var=None,
                       default_vars=None, other_vars=None):
    """
    從UI元素中收集輸入數據
    """
    logger.debug("開始收集用戶輸入資料")
    input_data = {}

    if use_name.get():
        input_data["name"] = name_var.get().strip()
    if use_id.get():
        input_data["id"] = id_var.get().strip()
    if use_phone.get():
        input_data["phone"] = phone_var.get().strip()
    if use_birth.get():
        input_data["birth"] = birth_var.get().strip()
    if use_custom.get():
        input_data["custom"] = custom_var.get().strip()

    # 讀取數字位數限制 (提供預設值)
    if digit_var is not None:
        digit_value = digit_var.get()
        if custom_digit_var is not None and digit_value == "custom":
            input_data["digit_length"] = custom_digit_var.get().strip()
        else:
            input_data["digit_length"] = digit_value
    else:
        input_data["digit_length"] = "4"  # 預設值

    # 讀取英數混合模式設定 (提供預設值)
    input_data["mix_mode"] = mixed_var.get() if mixed_var is not None else False
    input_data["english_position"] = english_position_var.get() if english_position_var is not None else "前"
    input_data["fixed_eng"] = fixed_eng_var.get().strip() if fixed_eng_var is not None else ""
    input_data["fixed_num"] = fixed_num_var.get().strip() if fixed_num_var is not None else ""

    # 設定條件 (提供預設值)
    input_data["default_conditions"] = {k: v.get() for k, v in default_vars.items()} if default_vars is not None else {}
    input_data["other_conditions"] = {k: v.get() for k, v in other_vars.items()} if other_vars is not None else {}

    # 驗證是否有勾選輸入選項
    from controller.analysis_controller import validate_analysis_input
    is_valid, errors = validate_analysis_input(input_data)
    if not is_valid:
        # 處理驗證錯誤
        pass

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
#     input_data["fixed_eng"] = fixed_eng_var.get().strip()
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

def save_input_history(input_data, file_manager):
    """
    保存輸入歷史

    Args:
        input_data (dict): 輸入數據
        file_manager: 文件管理器

    Returns:
        bool: 是否成功保存
    """
    try:
        # 確定輸入類型
        input_type = None
        value = None

        if "name" in input_data and input_data["name"]:
            input_type = "name"
            value = input_data["name"]
        elif "id" in input_data and input_data["id"]:
            input_type = "id"
            value = input_data["id"]
        elif "custom" in input_data and input_data["custom"]:
            input_type = "custom"
            value = input_data["custom"]
        else:
            logger.warning("保存輸入歷史失敗: 無有效輸入")
            return False

        # 準備要保存的歷史記錄數據
        history_data = {
            "value": value,
            "timestamp": None,  # file_manager.save_history會自動添加時間戳
            "settings": {
                "digit_length": input_data.get("digit_length"),
                "custom_digit": input_data.get("custom_digit"),
                "mix_mode": input_data.get("mix_mode"),
                "english_position": input_data.get("english_position"),
                "fixed_eng": input_data.get("fixed_eng"),
                "fixed_num": input_data.get("fixed_num"),
                "default_conditions": input_data.get("default_conditions", {}),
                "other_conditions": input_data.get("other_conditions", {})
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