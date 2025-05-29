# utils/validators.py
import re


def is_valid_id(id_str):
    """檢查身分證格式是否正確（台灣格式）"""
    return bool(re.match(r"^[A-Z][12]\d{8}$", id_str))


def is_valid_digit_length(s):
    """檢查自訂數字位數是否為正整數"""
    return s.isdigit() and int(s) > 0


def is_valid_fixed_eng(s):
    """檢查固定英文是否為 1~2 個英文字母"""
    return s == "" or (s.isalpha() and len(s) <= 2)


def is_valid_fixed_num(s):
    """檢查固定數字是否為 1~4 位數字"""
    return s == "" or (s.isdigit() and len(s) <= 4)


def validate_all(input_data):
    """整合所有檢查，回傳錯誤訊息清單"""
    errors = []

    if "id" in input_data and not is_valid_id(input_data["id"]):
        errors.append("身分證格式錯誤，需為大寫字母 + 1/2 + 8 位數字")

    if input_data.get("digit_length") == "custom":
        if not is_valid_digit_length(input_data.get("custom_digit", "")):
            errors.append("自訂位數必須是正整數")

    if not is_valid_fixed_eng(input_data.get("fixed_eng", "")):
        errors.append("固定英文必須為 1~2 個英文字母")

    if not is_valid_fixed_num(input_data.get("fixed_num", "")):
        errors.append("固定數字必須為 1~4 位數字")

    return errors
