#  input_controller.py

from ui.settings_module import (
    digit_var, custom_digit_var,
    mixed_var, english_position_var,
    fixed_eng_var, fixed_num_var,
    default_vars, other_vars
)
#  from core.number_analyzer import analyze_number

def collect_input_data(name_var, id_var, custom_var, use_name, use_id, use_custom):
    input_data = {}

    if use_name.get():
        input_data["name"] = name_var.get().strip()
    if use_id.get():
        input_data["id"] = id_var.get().strip()
    if use_custom.get():
        input_data["custom"] = custom_var.get().strip()

    digit_value = digit_var.get()
    input_data["digit_length"] = (
        custom_digit_var.get().strip() if digit_value == "custom" else digit_value
    )

    input_data["mix_mode"] = mixed_var.get()
    input_data["english_position"] = english_position_var.get()
    input_data["fixed_eng"] = fixed_eng_var.get().strip()
    input_data["fixed_num"] = fixed_num_var.get().strip()
    input_data["default_conditions"] = {k: v.get() for k, v in default_vars.items()}
    input_data["other_conditions"] = {k: v.get() for k, v in other_vars.items()}

    return input_data
'''
def analyze_input(data):
    # 假資料模擬分析結果
    result = {
        "counts": {
            "天醫": 2,
            "五鬼": 1,
            "六煞": 0
        },
        "adjustments": [
            "(天醫-1)", "(絕命-1)"
        ],
        "summary": {
            "strengths": {
                "天醫": "賺錢有如神助、外型氣質俱佳",
                "五鬼": "鬼才洋溢、快速學習力"
            },
            "financial_strategy": {
                "天醫": "智慧投資，行善積福",
                "五鬼": "創新思維，謹慎投資"
            }
        }
    }
    return result
'''


# def analyze_input(data):
#     return analyze_number(data)

