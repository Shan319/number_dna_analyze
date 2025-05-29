# utils/validators.py
import re
from datetime import datetime

from data.input_data import InputData, InputType, FixDigitsPosition


def is_valid_name(s: str):
    """檢查是否符合中文格式"""
    return True


def is_valid_id(s: str):
    """檢查身分證格式是否正確（台灣格式）"""
    # return bool(re.match(r"^[A-Z][12]\d{8}$", id_str))
    # 字母對應代碼表（A=10, B=11, ..., Z=35）
    letters = {
        'A': "10",
        'B': "11",
        'C': "12",
        'D': "13",
        'E': "14",
        'F': "15",
        'G': "16",
        'H': "17",
        'I': "34",
        'J': "18",
        'K': "19",
        'L': "20",
        'M': "21",
        'N': "22",
        'O': "35",
        'P': "23",
        'Q': "24",
        'R': "25",
        'S': "26",
        'T': "27",
        'U': "28",
        'V': "29",
        'W': "32",
        'X': "30",
        'Y': "31",
        'Z': "33"
    }

    if len(s) != 10:
        return False  # 長度需等於 10
    if not s[0].isupper():
        return False  # 第 0 碼需為大寫英文字母
    if not s[1:].isdigit():
        return False  # 後 9 碼需為數字

    sex = int(s[1])
    if sex not in (1, 2):
        return False  # 第 1 碼需為 1 或 2

    s_replaced = letters[s[0]] + s[1:]
    weighted = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]

    check_num = sum(int(x) * w for x, w in zip(s_replaced, weighted))
    return check_num % 10 == 0


def is_valid_phone(s: str):
    """檢查電話是否符合格式"""
    return bool(re.match(r"^09\d{8}$", s))


def is_valid_birth(s: str):
    """檢查生日是否符合格式"""
    success = False
    try:
        date = datetime.strptime(s, "%Y/%m/%d")
        success = True
    except Exception as e:
        print(e)
    return success


def is_valid_custom(s: str):
    return s.isalnum()


def is_valid_digit_length(s: str | int):
    """檢查自訂數字位數是否為大於 1 的正整數"""
    if isinstance(s, str):
        if not s.isdigit():
            return False
        s = int(s)
    return s > 1


def is_valid_fixed_num(s: str):
    """檢查固定數字是否為 1~4 位數字"""
    return (s.isalnum() and 1 <= len(s) <= 4)


def validate_all(input_data: InputData):
    """整合所有檢查，回傳錯誤訊息清單"""
    errors = []
    input_type = input_data.input_type
    input_value = input_data.input_value
    if input_type == InputType.NONE or input_value == "":
        errors.append("請至少提供一種輸入數據（姓名、身分證、生日、手機或自定義）")
    elif input_type == InputType.NAME:
        if not is_valid_name(input_value):
            errors.append("姓名格式錯誤")
    elif input_type == InputType.ID:
        if not is_valid_id(input_value):
            errors.append("身分證格式錯誤，需為大寫字母 + {1/2} + 8 位數字，其中最後一碼為檢查碼")
    elif input_type == InputType.PHONE:
        if not is_valid_phone(input_value):
            errors.append("電話格式錯誤")
    elif input_type == InputType.BIRTH:
        if not is_valid_birth(input_value):
            errors.append("生日格式錯誤，需為 yyyy/mm/dd")
    elif input_type == InputType.CUSTOM:
        if not is_valid_custom(input_value):
            errors.append("自定義格式錯誤")

    if not is_valid_digit_length(input_data.digits_length):
        errors.append("自訂位數必須是大於 1 的正整數")
        digits_length = float("inf")
    else:
        digits_length = int(input_data.digits_length)

    if input_data.fixed_digits_position != FixDigitsPosition.NONE:
        if not is_valid_fixed_num(input_data.fixed_digits_value):
            errors.append("固定英數字必須為 1~4 位")
        elif len(input_data.fixed_digits_value) >= digits_length:
            errors.append("固定英數字的長度應比總位數小 2 位以上")

    return errors
