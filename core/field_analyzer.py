'''
(輸出格式暫定，只是為了方便除錯以及數字分析引擎使用)
此為有英數混合的版本
需先pip install cryptography與下載附檔character.txt並更改路徑名稱
'''

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
# 個人端路徑(請更改)
stroke_dict = load_stroke_dict_from_file("C:\\Users\\vanes\\OneDrive\\桌面\\characters.txt")

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
def encrypt(text): return fernet.encrypt(text.encode()).decode()
def decrypt(token): return fernet.decrypt(token.encode()).decode()

# 數字轉配對組合規則
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
    pairs = []
    for i in range(len(number_str) - 1):
        a, b = number_str[i], number_str[i+1]
        if (a == '0' and b != '5') or (b == '0' and a != '5'):
            pair = b*2 if a == '0' else a*2
        elif (a == '5' and b == '0') or (a == '0' and b == '5'):
            pair = "00"
        elif a == '5' or b == '5':
            pair = b*2 if a == '5' else a*2
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

# 格式驗證
def verify_twid(idstr):
    if len(idstr) != 10 or not idstr[0].isupper() or not idstr[1:].isdigit() or idstr[1] not in ('1', '2'):
        return False
    cmap = [10,11,12,13,14,15,16,17,34,18,19,20,21,22,35,23,24,25,26,27,28,29,32,30,31,33]
    num1 = cmap[ord(idstr[0]) - ord('A')]
    newid = str(num1) + idstr[1:]
    weight = [1,9,8,7,6,5,4,3,2,1,1]
    return sum(int(newid[i]) * weight[i] for i in range(11)) % 10 == 0

def is_valid_mobile(m): return re.fullmatch(r"09\d{8}", m)
def is_valid_date_format(d): return re.fullmatch(r"\d{4}/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])", d)

# 歷史紀錄
def get_history_filename(type_code):
    return {
        "1": "birthday_history.enc",
        "2": "mobile_history.enc",
        "3": "id_history.enc",
        "4": "name_history.enc",
        "5": "mixed_history.enc"
    }.get(type_code, "unknown.enc")

def save_to_history(data, type_code):
    with open(get_history_filename(type_code), "a", encoding="utf-8") as f:
        f.write(encrypt(data) + "\n")

def load_history(type_code):
    filename = get_history_filename(type_code)
    if not os.path.exists(filename): return []
    with open(filename, "r", encoding="utf-8") as f:
        return [decrypt(line.strip()) for line in f]

def write_history(data_list, type_code):
    with open(get_history_filename(type_code), "w", encoding="utf-8") as f:
        for data in data_list:
            f.write(encrypt(data) + "\n")

def delete_history(type_code):
    history = load_history(type_code)
    if not history:
        print("沒有資料可刪除。")
        return
    for idx, item in enumerate(history, 1):
        print(f"{idx}: {item}")
    choice = input("輸入要刪除的編號，或輸入 all 來刪除全部：").strip().lower()
    if choice == "all":
        write_history([], type_code)
    elif choice.isdigit() and 1 <= int(choice) <= len(history):
        del history[int(choice)-1]
        write_history(history, type_code)
    else:
        print("格式不符")

# 主程式
def main():
    print("請選擇操作模式：\n1. 分析磁場\n2. 刪除歷史資料")
    choice = input("請輸入選項代碼（1或2）：").strip()

    if choice == "2":
        print("選擇類別：1.生日 2.手機 3.身分證 4.姓名 5.英數混合")
        delete_choice = input("請輸入類別代碼：").strip()
        delete_history(delete_choice)
        return

    elif choice != "1":
        print("無效的選項。")
        return

    print("請選擇輸入類型：\n1. 生日\n2. 手機\n3. 身分證\n4. 姓名\n5. 英數混合")
    choice_input = input("請輸入代碼（1~5）：").strip()

    def select_from_history():
        history = load_history(choice_input)
        if not history:
            print("無歷史資料可用")
            return None
        print("請選擇歷史資料：")
        for idx, item in enumerate(history, 1):
            print(f"{idx}: {item}")
        idx = input("輸入編號選擇，或按 Enter 取消：").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(history):
            return history[int(idx) - 1]
        return None

    use_history = input("是否使用歷史資料？(Y/N)：").strip().upper() == "Y"
    selected_data = None

    if use_history:
        selected_data = select_from_history()
        if not selected_data:
            print("取消選擇歷史資料，請手動輸入。")
            use_history = False

    if choice_input == "1":
        birth = selected_data if use_history else input("請輸入生日（YYYY/MM/DD）：").strip()
        if not is_valid_date_format(birth):
            print("日期格式錯誤")
            return
        result = analyze_input(birth.replace("/", ""))
        print("分析結果：", result)
        if not use_history and input("是否儲存紀錄？(Y/N)：").strip().upper() == "Y":
            save_to_history(birth, "1")

    elif choice_input == "2":
        mobile = selected_data if use_history else input("請輸入手機號碼：").strip()
        if not is_valid_mobile(mobile):
            print("手機格式錯誤")
            return
        result = analyze_input(mobile)
        print("分析結果：", result)
        if not use_history and input("是否儲存紀錄？(Y/N)：").strip().upper() == "Y":
            save_to_history(mobile, "2")

    elif choice_input == "3":
        id_number = selected_data if use_history else input("請輸入身分證號：").strip().upper()
        if not verify_twid(id_number):
            print("身分證格式錯誤")
            return
        result = analyze_input(id_number, is_id=True)
        print("分析結果：", result)
        if not use_history and input("是否儲存紀錄？(Y/N)：").strip().upper() == "Y":
            save_to_history(id_number, "3")

    elif choice_input == "4":
        name = selected_data if use_history else input("請輸入姓名：").strip()
        result = analyze_name_strokes(name)
        print("分析結果：", result)
        if not use_history and input("是否儲存紀錄？(Y/N)：").strip().upper() == "Y":
            save_to_history(name, "4")

    elif choice_input == "5":
        mixed = selected_data if use_history else input("請輸入英數字混合字串：").strip()
        result = analyze_mixed_input(mixed)
        print("分析結果：", result)
        if not use_history and input("是否儲存紀錄？(Y/N)：").strip().upper() == "Y":
            save_to_history(mixed, "5")

    else:
        print("無效代碼")
        return

    if input("是否查看歷史紀錄？(Y/N)：").strip().upper() == "Y":
        history = load_history(choice_input)
        print("歷史資料：")
        for idx, item in enumerate(history, 1):
            print(f"{idx}: {item}")


if __name__ == "__main__":
    main()
