# utils/validators.py
import re

from data.input_data import InputData, InputType, FixDigitsPosition


def is_valid_id(id_str):
    """檢查身分證格式是否正確（台灣格式）"""
    return bool(re.match(r"^[A-Z][12]\d{8}$", id_str))


def is_valid_digit_length(s: str):
    """檢查自訂數字位數是否為正整數"""
    return s.isdigit() and int(s) > 0


def is_valid_fixed_num(s: str):
    """檢查固定數字是否為 1~4 位數字"""
    return (s.isalnum() and 1 <= len(s) <= 4)


def validate_all(input_data: InputData):
    """整合所有檢查，回傳錯誤訊息清單"""
    errors = []
    if input_data.input_type == InputType.NONE or input_data.input_value == "":
        errors.append("請至少提供一種輸入數據（姓名、身分證、生日、手機或自定義）")
    elif input_data.input_type == InputType.NAME:
        pass
    elif input_data.input_type == InputType.ID:
        if not is_valid_id(input_data.input_value):
            errors.append("身分證格式錯誤，需為大寫字母 + 1/2 + 8 位數字")
    elif input_data.input_type == InputType.PHONE:
        pass
    elif input_data.input_type == InputType.BIRTH:
        pass
    elif input_data.input_type == InputType.CUSTOM:
        pass

    if input_data.digits_length <= 0:
        errors.append("自訂位數必須是正整數")

    if input_data.fixed_digits_position != FixDigitsPosition.NONE:
        if not is_valid_fixed_num(input_data.fixed_digits_value):
            errors.append("固定數字必須為 1~4 位英數字")

    return errors
