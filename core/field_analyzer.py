
'''
(輸出格式暫定，只是為了方便除錯以及數字分析引擎使用)
需先pip install cryptography與下載附檔character.txt並更改路徑名稱

磁場組合對應表
'''

from cryptography.fernet import Fernet   # 需先下載cryptography >pip install cryptography  
import os
import re

# 讀取中文筆劃檔(在個人電腦上，請參考附檔character.txt)
def load_stroke_dict_from_file(filename):
    stroke_dict = {}
    with open(filename, "r", encoding="cp950", errors="ignore") as f:
        lines = f.readlines()

    for line in lines:
        # 跳過說明或空行
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
# 替換stroke_dict路徑
stroke_dict = load_stroke_dict_from_file("C:\\Users\\vanes\\OneDrive\\桌面\\characters.txt")

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

# 保護使用者資料
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

# 分析數字規則並分組
def transform_numbers(number_str):
    def handle_5_between_9_1(s):
        result = ''
        i = 0
        while i < len(s) - 2:
            if s[i] == '9' and s[i+1] == '5' and s[i+2] == '1':
                result += '91' + '91'
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
            number_str = number_str[1]*2 + number_str[1:]
        if number_str[-1] == '5':
            number_str = number_str[:-2] + number_str[-2]*2
    # 0和5的特殊情形
    pairs = []
    for i in range(len(number_str) - 1):
        a, b = number_str[i], number_str[i+1]
        if (a == '0' and b != '5') or (b == '0' and a != '5'):
            pair = b*2 if a == '0' else a*2
        elif a == '5' and b == '0' or a == '0' and b == '5':
            pair = "00"
        elif a == '5' or b == '5':
            pair = b*2 if a == '5' else a*2
        else:
            pair = a + b
        pairs.append(pair)
    return pairs

# debug用，若程式無法判別磁場名稱，會返回未知
def get_name_from_pair(pair):
    for name, group in name_map.items():
        if pair in group:
            return name
    return "未知"

# 將輸入的數字分成兩兩一組的磁場名稱
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

# 分析姓名筆劃，筆劃會被轉為一整串數字後兩兩分組，如：4111 -> 41, 11, 11
def analyze_name_strokes(name_str):
    strokes = []
    for char in name_str:
        if char in stroke_dict:
            strokes.append(str(stroke_dict[char]))
        else:
            print(f"無法辨識字元「{char}」，請擴充 stroke_dict。")
            return
    print("筆劃：", ' '.join(strokes))
    stroke_string = ''.join(strokes)  # 例如：['4','1','11'] -> '4111'
    pairs = transform_numbers(stroke_string)
    print("配對：", ' '.join(pairs))
    results = [get_name_from_pair(pair) for pair in pairs]
    print("筆劃組合結果：", ' '.join(results))


# 台灣身份證字號checksum(防呆)
def verify_twid(idstr):
    if len(idstr) != 10:
        return False
    if not idstr[0].isupper() or not idstr[1:].isdigit():
        return False
    if idstr[1] not in ('1', '2'):
        return False
    cmap = [10, 11, 12, 13, 14, 15, 16, 17, 34, 18, 19, 20,
            21, 22, 35, 23, 24, 25, 26, 27, 28, 29, 32, 30, 31, 33]
    num1 = cmap[ord(idstr[0]) - ord('A')]
    newid = str(num1) + idstr[1:]
    weight = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]
    checksum = sum(int(newid[i]) * weight[i] for i in range(11))
    return checksum % 10 == 0

# 確認使用者輸入的日期、手機號(台灣)正確
def is_valid_date_format(date_str):
    return bool(re.fullmatch(r"\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])", date_str))

def is_valid_mobile(mobile_str):
    return bool(re.fullmatch(r"09\d{8}", mobile_str))

# 儲存使用者資料
def save_to_history(birthday, mobile, identity, name_input):
    with open("history.enc", "a", encoding="utf-8") as f:
        encrypted_data = encrypt(f"{birthday},{mobile},{identity},{name_input}")
        f.write(encrypted_data + "\n")

def load_history():
    if not os.path.exists("history.enc"):
        return []
    with open("history.enc", "r", encoding="utf-8") as f:
        history = []
        for line in f:
            data = decrypt(line.strip()).split(",")
            print(f"讀取的資料：{data}")
            if len(data) == 4:
                history.append(tuple(data))
            else:
                print(f"無效的歷史資料：{line.strip()}")
        return history

def write_history(data):
    with open("history.enc", "w", encoding="utf-8") as f:
        for entry in data:
            f.write(encrypt(",".join(entry)) + "\n")

def delete_history():
    history = load_history()
    if not history:
        print("沒有資料可刪除。")
        return
    for idx, (b, m, i, n) in enumerate(history, 1):
        print(f"{idx}: 生日={b}, 手機={m}, 身分證={i}, 姓名={n}")
    print("輸入要刪除的編號，或輸入 all 來刪除全部。")
    choice = input("請輸入：").strip().lower()
    if choice == "all":
        write_history([])
        print("已刪除所有歷史資料。")
    elif choice.isdigit() and 1 <= int(choice) <= len(history):
        del history[int(choice)-1]
        write_history(history)
        print("已刪除指定資料。")
    else:
        print("格式不符")

# 實作主程式流程
def main():
    print("選擇操作：")
    print("1. 使用先前輸入的資料")
    print("2. 輸入新資料")
    print("3. 刪除歷史資料")

    choice = input("請輸入 1、2 或3：").strip()

    if choice == "1":
        history = load_history()
        if not history:
            print("尚無歷史資料，請改用新資料。")
            return main()
        for idx, (b, m, i, n) in enumerate(history, 1):
            print(f"{idx}: 生日={b}, 手機={m}, 身分證={i}, 姓名={n}")
        index = input("請選擇編號使用：").strip()
        if not index.isdigit() or not (1 <= int(index) <= len(history)):
            print("格式不符")
            return
        birthday, mobile, identity, name_input = history[int(index)-1]

    elif choice == "2":
        birthday = input("輸入生日(格式YYYY/MM/DD)：").strip()
        if not is_valid_date_format(birthday):
            print("格式不符")
            return
        mobile = input("輸入手機號碼(格式：0912345678)：").strip()
        if not is_valid_mobile(mobile):
            print("格式不符")
            return
        identity = input("輸入身分證字號(格式：A123456789)：").strip()
        if not verify_twid(identity):
            print("格式不符")
            return
        name_input = input("若欲分析姓名筆劃，請輸入姓名：").strip()
        consent = input("是否儲存本次輸入資料？(Y/N)：").strip().upper()
        if consent == "Y":
            save_to_history(birthday, mobile, identity, name_input)

    elif choice == "3":
        delete_history()
        return
    else:
        print("格式不符")
        return main()

    print("選擇操作：")
    print("1. 分析")
    print("2. 退出")

    operation_choice = input("請輸入 1 或 2：").strip()

    if operation_choice == "1":
        print(analyze_input(birthday.replace("/", "")))
        print(analyze_input(mobile))
        print(analyze_input(identity, is_id=True))
        analyze_name_strokes(name_input)
    else:
        print("退出中...")

if __name__ == "__main__":
    main()
