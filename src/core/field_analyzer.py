#  core/field_analyzer.py

from src.utils import main_service


class FieldAnalyzer:
    """磁場分析器。

    可由計算 input value 得到他目前所對應的磁場名稱。
    """

    def __init__(self) -> None:
        self.logger = main_service.log.get_logger("數字 DNA 分析器.FieldAnalyzer")

    # 磁場對應表
    NAME_MAP = {
        "伏位": {"00", "11", "22", "33", "44", "66", "77", "88", "99"},
        "延年": {"19", "91", "78", "87", "43", "34", "26", "62"},
        "生氣": {"14", "41", "67", "76", "93", "39", "28", "82"},
        "天醫": {"13", "31", "68", "86", "94", "49", "72", "27"},
        "六煞": {"16", "61", "74", "47", "38", "83", "92", "29"},
        "絕命": {"12", "21", "69", "96", "84", "48", "37", "73"},
        "禍害": {"17", "71", "98", "89", "64", "46", "32", "23"},
        "五鬼": {"18", "81", "97", "79", "36", "63", "42", "24"},
    }

    def get_name_from_pair(self, pair: str) -> str:
        for name, group in self.NAME_MAP.items():
            if pair in group:
                return name
        return "未知"

    _STROKE_DICT: dict[str, int] = {}

    # 讀取筆劃檔
    def get_stroke_dict(self) -> dict[str, int]:
        """取得中文字筆劃字典。

        這個方法確保筆劃檔不被重複讀取。

        Returns
        -------
        dict[str, int]
            中文字筆劃字典
        """
        if self.__class__._STROKE_DICT:
            return self.__class__._STROKE_DICT

        self.logger.info(f"讀取中文字筆劃檔")

        stroke_dict = {}
        characters_path = main_service.file_manager.get_characters_path()
        with open(characters_path, "r", encoding="cp950", errors="ignore") as f:
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
                    self.logger.warning(f"無法解析行: {line.strip()} 錯誤: {e}")

        self.__class__._STROKE_DICT = stroke_dict
        return stroke_dict

    # 數字轉配對組合規則
    def handle_5_between_9_1(self, s: str) -> str:
        """處理數字字串中的 "159" 及 "951" 的狀況

        Parameters
        ----------
        s : str
            原數字字串

        Returns
        -------
        str
            新字串。遇到 "159" 就改為 "1919"，遇到 "951" 就改為 "9191"。
        """
        result = ''
        i = 0
        while i < len(s) - 2:
            if s[i] == '9' and s[i + 1] == '5' and s[i + 2] == '1':
                result += '91' + '91'
                i += 3
            elif s[i] == '1' and s[i + 1] == '5' and s[i + 2] == '9':
                result += '19' + '19'
                i += 3
            else:
                result += s[i]
                i += 1
        result += s[i:]
        return result

    def transform_numbers(self, number_str: str) -> list[str]:
        """轉換數字。

        依照特殊規則將數字兩兩配對為數對。

        Parameters
        ----------
        number_str : str
            原數字字串

        Returns
        -------
        list[str]
            結果數字字串，每一個元素皆為 2 碼的數字字串
        """
        # 處理 "159" 及 "951" 的狀況
        number_str = self.handle_5_between_9_1(number_str)

        # 將中間的 5 全部移除
        if len(number_str) > 2:
            number_str = number_str[0] + number_str[1:-1].replace('5', '') + number_str[-1]

        # [?] 若 5 在首尾則捨棄 5 後再將相鄰數字重複一次
        if len(number_str) >= 2:
            if number_str[0] == '5':
                number_str = number_str[1] * 2 + number_str[1:]
            if number_str[-1] == '5':
                number_str = number_str[:-2] + number_str[-2] * 2

        # 配對
        pairs: list[str] = []
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

    def analyze_input(self, input_str: str, is_id=False) -> str:
        if is_id:
            letter = input_str[0]
            number = input_str[1:]
            letter_num = f"{ord(letter.upper()) - ord('A') + 1:02d}"
            input_str = letter_num + number
        else:
            input_str = input_str.replace("/", "")
        final_pairs = self.transform_numbers(input_str)
        names = [self.get_name_from_pair(pair) for pair in final_pairs]
        return " ".join(names)

    def analyze_name_strokes(self, name_str: str) -> str | None:
        strokes: list[str] = []

        # 載入筆劃字典
        stroke_dict = self.get_stroke_dict()
        for char in name_str:
            if char in stroke_dict:
                strokes.append(str(stroke_dict[char]))
            else:
                self.logger.warning(f"無法辨識字元「{char}」，請擴充 stroke_dict。")
                return None
        stroke_string = ''.join(strokes)
        pairs = self.transform_numbers(stroke_string)
        results = [self.get_name_from_pair(pair) for pair in pairs]
        return " ".join(results)

    def analyze_mixed_input(self, mixed_str: str) -> str:
        result = ""
        for ch in mixed_str.upper():
            if ch.isalpha():
                result += f"{ord(ch) - ord('A') + 1:02d}"
            elif ch.isdigit():
                result += ch
            else:
                continue
        pairs = self.transform_numbers(result)
        return " ".join(self.get_name_from_pair(pair) for pair in pairs)
