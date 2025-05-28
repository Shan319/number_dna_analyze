#  core/field_analyzer.py

from cryptography.fernet import Fernet
import os
import re


# 讀取筆劃檔
def load_stroke_dict_from_file(filename):
    stroke_dict = {}
    with open(filename, "r", encoding="cp950", errors="ignore") as f:
        for line in f:
            if not line.strip() or line.startswith("Column"):
                continue
            try:
                parts = line.strip().split()
                if len(parts) >= 2:
                    char = parts[0]
                    stroke = int(parts[-1])
                    stroke_dict[char] = stroke
            except Exception as e:
                print(f"無法解析行: {line.strip()} 錯誤: {e}")
    return stroke_dict


# 獲取專案目錄路徑
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 資源文件的路徑
characters_path = os.path.join(base_dir, "resources", "characters.txt")

# 載入筆劃字典
stroke_dict = load_stroke_dict_from_file(characters_path)

# 磁場對應表
name_map = {
    "伏位": {"00", "11", "22", "33", "44", "66", "77", "88", "99"},
    "延年": {"19", "91", "78", "87", "43", "34", "26", "62"},
    "生氣": {"14", "41", "67", "76", "93", "39", "28", "82"},
    "天醫": {"13", "31", "68", "86", "94", "49", "72", "27"},
    "六煞": {"16", "61", "74", "47", "38", "83", "92", "29"},
    "絕命": {"12", "21", "69", "96", "84", "48", "37", "73"},
    "禍害": {"17", "71", "98", "89", "64", "46", "32", "23"},
    "五鬼": {"18", "81", "97", "79", "36", "63", "42", "24"},
}


# 加密保護
def load_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as f:
            f.write(key)
    else:
        with open("key.key", "rb") as f:
            key = f.read()
    return Fernet(key)


fernet = load_key()


def encrypt(text):
    return fernet.encrypt(text.encode()).decode()


def decrypt(token):
    return fernet.decrypt(token.encode()).decode()


# 數字轉配對組合規則
def transform_numbers(number_str):

    def handle_5_between_9_1(s):
        result = ''
        i = 0
        while i < len(s) - 2:
            if s[i] == '9' and s[i + 1] == '5' and s[i + 2] == '1':
                result += '91' + '91'
                i += 3
            elif s[i] == '1' and s[i+1] == '5' and s[i+2] == '9':
                result += '19' + '19'
                i += 3
            else:
                result += s[i]
                i += 1
        result += s[i:]
        return result

    number_str = handle_5_between_9_1(number_str)
    if len(number_str) > 2:
        number_str = number_str[0] + number_str[1:-1].replace('5', '') + number_str[-1]
    if len(number_str) >= 2:
        if number_str[0] == '5':
            number_str = number_str[1] * 2 + number_str[1:]
        if number_str[-1] == '5':
            number_str = number_str[:-2] + number_str[-2] * 2
    pairs = []
    for i in range(len(number_str) - 1):
        a, b = number_str[i], number_str[i + 1]
        if (a == '0' and b != '5') or (b == '0' and a != '5'):
            pair = b * 2 if a == '0' else a * 2
        elif (a == '5' and b == '0') or (a == '0' and b == '5'):
            pair = "00"
        elif a == '5' or b == '5':
            pair = b * 2 if a == '5' else a * 2
        else:
            pair = a + b
        pairs.append(pair)
    return pairs


def get_name_from_pair(pair):
    for name, group in name_map.items():
        if pair in group:
            return name
    return "未知"


def analyze_input(input_str, is_id=False):
    if is_id:
        letter = input_str[0]
        number = input_str[1:]
        letter_num = f"{ord(letter.upper()) - ord('A') + 1:02d}"
        input_str = letter_num + number
    else:
        input_str = input_str.replace("/", "")
    final_pairs = transform_numbers(input_str)
    names = [get_name_from_pair(pair) for pair in final_pairs]
    return " ".join(names)


def analyze_name_strokes(name_str):
    strokes = []
    for char in name_str:
        if char in stroke_dict:
            strokes.append(str(stroke_dict[char]))
        else:
            print(f"無法辨識字元「{char}」，請擴充 stroke_dict。")
            return
    stroke_string = ''.join(strokes)
    pairs = transform_numbers(stroke_string)
    results = [get_name_from_pair(pair) for pair in pairs]
    return " ".join(results)


def analyze_mixed_input(mixed_str):
    result = ""
    for ch in mixed_str.upper():
        if ch.isalpha():
            result += f"{ord(ch) - ord('A') + 1:02d}"
        elif ch.isdigit():
            result += ch
        else:
            continue
    pairs = transform_numbers(result)
    return " ".join(get_name_from_pair(pair) for pair in pairs)


