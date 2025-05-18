#data/rule_repository.py
"""
規則庫 - 管理易經數字規則資料，作為其他模組獲取規則數據的中央存儲庫。

負責載入、管理並提供「數字 DNA 分析器」應用程式所使用的規則定義
，包括基本數字意義、八大磁場規則和相應的算法。
其處理事項包含：
從 JSON 檔案載入規則資料
快取規則資料以提升效能
提供簡潔的介面以存取規則
管理規則版本與更新
"""
import os
import json
from utils.config import config
import logging

# Setup logging
logger = logging.getLogger(__name__)

class RuleRepository:
    """易經數字規則庫，管理和提供所有數字規則資料"""

    def __init__(self, rules_dir: str = "resources/rules"):
        """
        Initialize the rule repository.

        Args:
            rules_dir: Directory path containing the rule JSON files
        """
        # 基本路徑設置
        self.rules_dir = rules_dir
        self.base_rules_path = os.path.join(rules_dir, "base_rules.json")
        self.field_rules_path = os.path.join(rules_dir, "field_rules.json")

        # 讀取規則數據
        self._base_rules = None
        self._field_rules = None
        self._field_pairs_lookup = None  # 用於快速查詢磁場
        self._field_strength_lookup = None  # 用於快速查詢強度

        # 從基本規則中提取的常用資料
        self.number_meanings = {}  # 數字意義
        self.number_elements = {}  # 數字五行屬性
        self.number_energy = {}    # 數字陰陽屬性
        self.number_combinations = {}  # 數字組合效果

        # 從磁場規則中提取的常用資料
        self.field_types = {}            # 磁場類型
        self.neutralization_rules = {}   # 化解規則

        # 整合的磁場對應表
        self._magnetic_field_map = {
            "伏位": {"11", "22", "33", "44", "66", "77", "88", "99"},
            "延年": {"19", "91", "78", "87", "43", "34", "26", "62"},
            "生氣": {"14", "41", "67", "76", "93", "39", "28", "82"},
            "天醫": {"13", "31", "68", "86", "94", "49", "72", "27"},
            "六煞": {"16", "61", "74", "47", "38", "83", "92", "29"},
            "絕命": {"12", "21", "69", "96", "84", "48", "37", "73"},
            "禍害": {"17", "71", "98", "89", "64", "46", "32", "23"},
            "五鬼": {"18", "81", "97", "79", "36", "63", "42", "24"}
        }

        # 整合的磁場關鍵字
        self._field_keywords = {
            "伏位": {"蓄勢待發", "狀況延續", "臥虎藏龍"},
            "生氣": {"貴人", "轉機", "好名聲"},
            "天醫": {"主大才", "天生聰穎", "文筆好"},
            "延年": {"意志堅定的領袖格局"},
            "絕命": {"高IQ低EQ", "大起大落的極端特質"},
            "禍害": {"口舌", "病弱", "心機"},
            "五鬼": {"最有才華但最不穩定", "際遇波折"},
            "六煞": {"情感", "婚姻", "或人際關係方面糾葛"}
        }

        # 載入規則
        self._load_rules()

    def _load_rules(self):
        """
        Load rules from JSON files and initialize lookups.
        從JSON文件加載規則並初始化查詢表。
        """
        try:
            # 載入基本規則
            if os.path.exists(self.base_rules_path):
                with open(self.base_rules_path, 'r', encoding='utf-8') as f:
                    self._base_rules = json.load(f)
                logger.info(f"Base rules loaded from {self.base_rules_path}")

                # 提取基本規則數據到專用變數
                self.number_meanings = self._base_rules.get("number_meanings", {})
                self.number_elements = self._base_rules.get("number_elements", {})
                self.number_energy = self._base_rules.get("number_energy", {})
                self.number_combinations = self._base_rules.get("number_combinations", {})
            else:
                logger.warning(f"Base rules file not found at {self.base_rules_path}")
                self._base_rules = {}

            # 載入磁場規則
            if os.path.exists(self.field_rules_path):
                with open(self.field_rules_path, 'r', encoding='utf-8') as f:
                    self._field_rules = json.load(f)
                logger.info(f"Field rules loaded from {self.field_rules_path}")

                # 提取磁場規則數據到專用變數
                self.field_types = self._field_rules.get("field_types", {})
                self.neutralization_rules = self._field_rules.get("neutralization_rules", {})
            else:
                logger.warning(f"Field rules file not found at {self.field_rules_path}")
                self._field_rules = {}

            # 初始化查詢表，提高訪問速度
            self._build_field_lookups()

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading rules: {e}")
            raise RuntimeError(f"Failed to load rules: {e}")

    def _build_field_lookups(self) -> None:
        """
        Build lookup tables for quick access to field data.
        建立快速查詢表以便快速訪問磁場數據。
        """
        self._field_pairs_lookup = {}
        self._field_strength_lookup = {}

        if not self._field_rules:
            # 如果沒有載入磁場規則，則使用hard_code的磁場數據
            for field_name, pairs in self._magnetic_field_map.items():
                for pair in pairs:
                    self._field_pairs_lookup[pair] = {
                        "fieldId": field_name.lower().replace("磁場", ""),
                        "fieldName": field_name
                    }
            return

        # 從磁場規則中建立查詢表
        for field_group in self._field_rules.get("fieldGroups", []):
            field_id = field_group.get("groupId")
            field_name = field_group.get("groupName")

            # 將每個數字對映射到其磁場
            for pair in field_group.get("fieldPairs", []):
                self._field_pairs_lookup[pair] = {
                    "fieldId": field_id,
                    "fieldName": field_name
                }

            # 映射強度等級
            strength_levels = field_group.get("strengthLevels", {})
            for level, pairs in strength_levels.items():
                level_value = int(level.replace("level", ""))
                for pair in pairs:
                    self._field_strength_lookup[pair] = {
                        "fieldId": field_id,
                        "fieldName": field_name,
                        "strengthLevel": level_value
                    }

    def reload_rules(self) -> bool:
        """
        載入規則檔案
        Load rules from JSON files and initialize lookups.
        Args:
            file_path: 規則文件路徑

        Returns:
            規則數據，若載入失敗則回傳空字典

        """
        try:
            self._load_rules()
            logger.info("Rules successfully reloaded")
            return json.load(f)
        except Exception as e:
            logger.error(f"載入規則文件 {file_path} 失敗: {e}")
            return {}

    #  def __init__(self):
        """初始化規則庫，載入規則數據"""
        # 載入基本規則和磁場規則
        self.base_rules = self._load_rules(config.get_base_rules_path())
        self.field_rules = self._load_rules(config.get_field_rules_path())

        # 從基本規則中提取數字意義
        self.number_meanings = self.base_rules.get("number_meanings", {})  # 數字意義
        self.number_elements = self.base_rules.get("number_elements", {})  # 數字五行屬性
        self.number_energy = self.base_rules.get("number_energy", {})      # 數字陰陽屬性
        self.number_combinations = self.base_rules.get("number_combinations", {})  # 數字組合

        # 從磁場規則中提取八大磁場定義
        self.field_types = self.field_rules.get("field_types", {})          # 磁場類型
        self.neutralization_rules = self.field_rules.get("neutralization_rules", {})  # 化解規則

    # def _load_rules(self, file_path):
        """載入規則檔案
        Load rules from JSON files and initialize lookups.
        Args:
            file_path: 規則文件路徑

        Returns:
            規則數據，若載入失敗則回傳空字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"載入規則文件 {file_path} 失敗: {e}")
            return {}
    def get_number_conversion_rules(self):
        """
        Get rules for converting and preprocessing numbers.
        獲取數字轉換和預處理規則。

        Returns:
            Dictionary containing number conversion rules
            包含數字轉換規則的字典
        """
        if not self._base_rules:
            # 如果沒有載入基本規則，返回默認的轉換規則
            return {
                "name": "numberPreprocessing",
                "description": "規則：數字轉換與預處理",
                "specialNumbers": {
                    "five": {
                        "atBoundary": "頭尾的5視為與相鄰數字相同",
                        "inMiddle": "中間的5跳過並合併前後數字",
                        "betweenOneAndNine": "在1和9之間的5處理後，重複前後數字"
                    },
                    "zero": "數字0視為與相鄰數字相同"
                }
            }

        # 從JSON規則檔案返回數字預處理規則
        preprocessing_rules = self._base_rules.get("numberPreprocessing", {})
        return preprocessing_rules

    def get_bit_partitioning_rules(self):
        """
        Get rules for dividing numbers into bit pairs.
        獲取數字劃分為位元對的規則。

        Returns:
            Dictionary containing bit partitioning rules
            包含位元劃分規則的字典
        """
        if not self._base_rules:
            # 如果沒有載入基本規則，返回默認的位元劃分規則
            return {
                "name": "bitPartitioning",
                "description": "規則：位元劃分",
                "method": "每兩位數字組成一個位元",
                "examples": "如1234567共有6個位元：12,23,34,45,56,67"
            }

        # 從JSON規則檔案返回位元劃分規則
        partitioning_rules = self._base_rules.get("bitPartitioning", {})
        return partitioning_rules

    def get_field_mapping_rules(self):
        """
        Get rules for mapping bit pairs to magnetic fields.
        獲取位元對應到磁場的規則。

        Returns:
            Dictionary containing field mapping rules
            包含磁場對應規則的字典
        """
        if not self._base_rules:
            # 如果沒有載入基本規則，使用磁場對應表

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

            # 使用磁場對應表創建規則字典
            field_mapping = {
                "name": "fieldMapping",
                "description": "規則：位元磁場判讀",
                "fieldDefinitions": {},
                "pairMappings": {}
            }

            # 將磁場對應表轉換為適合的格式
            for field_name, pairs in name_map.items():
                # 使用磁場名稱作為字典鍵
                field_key = field_name

                # 設置磁場定義
                field_mapping["fieldDefinitions"][field_key] = {
                    "name": field_name,
                    "pairs": list(pairs)
                }

                # 設置數字對應的磁場
                for pair in pairs:
                    field_mapping["pairMappings"][pair] = field_name

            # 添加獲取磁場名稱的方法定義
            field_mapping["methods"] = {
                "getFieldNameByPair": "根據數字對獲取對應的磁場名稱"
            }

            return field_mapping

        # 從JSON規則檔案返回磁場映射規則
        mapping_rules = self._base_rules.get("fieldMapping", {})

        # 若沒有 pairMappings，則建立
        if "pairMappings" not in mapping_rules and "fieldDefinitions" in mapping_rules:
            mapping_rules["pairMappings"] = {}
            for field_key, field_info in mapping_rules["fieldDefinitions"].items():
                if "pairs" in field_info:
                    field_name = field_info["name"]
                    for pair in field_info["pairs"]:
                        mapping_rules["pairMappings"][pair] = field_name

        return mapping_rules

    def get_field_name_by_pair(self, pair: str):
        """
        Get field name for a given bit pair.
        根據數字對應獲取磁場名稱。

        Args:
            pair: Two-digit pair to look up
            要查詢的兩位數對

        Returns:
            Field name, or "未知" if not found
            磁場名稱，若未找到則返回"未知"
        """
        # 獲取對應磁場
        mapping_rules = self.get_field_mapping_rules()

        # 嘗試從 pairMappings 中找到對應的磁場
        if "pairMappings" in mapping_rules and pair in mapping_rules["pairMappings"]:
            return mapping_rules["pairMappings"][pair]

        # 方案二:遍歷 fieldDefinitions
        if "fieldDefinitions" in mapping_rules:
            for field_key, field_info in mapping_rules["fieldDefinitions"].items():
                if "pairs" in field_info and pair in field_info["pairs"]:
                    return field_info["name"]

        # 方案三:磁場對應表
        for field_name, pairs in self._magnetic_field_map.items():
            if pair in pairs:
                return field_name

        return "未知"

    def get_energy_strength_rules(self):
        """
        Get rules for determining energy strength levels.
        獲取能量強度等級的規則。

        Returns:
            Dictionary containing energy strength rules
            包含能量強度規則的字典
        """
        if not self._base_rules:
            # 如果沒有載入基本規則，返回默認的能量強度規則
            strength_rules = {
                "name": "energyStrength",
                "description": "規則：位元磁場能量強度",
                "strengthLevels": {
                    "level3": "最高強度",
                    "level2": "高強度",
                    "level1": "中等強度",
                    "level0": "低強度"
                }
            }

            return strength_rules

        # 從JSON規則檔案返回能量強度規則
        strength_rules = self._base_rules.get("energyStrength", {})
        return strength_rules

    def get_number_fields(self, number_sequence):
        """分析數字序列中的磁場

        參數:
            number_sequence: 數字序列

        返回:
            包含各磁場數量的字典
        """
        # 初始化八大磁場計數
        fields = {
            "伏位": 0, "生氣": 0, "天醫": 0, "延年": 0,
            "絕命": 0, "禍害": 0, "五鬼": 0, "六煞": 0
        }

        # 檢查單個數字的磁場
        for digit in number_sequence:
            for field_name, field_info in self.field_types.items():
                for pattern in field_info.get("patterns", []):
                    if "digit" in pattern and pattern["digit"] == digit:
                        fields[field_name] += pattern.get("value", 1)

        # 檢查數字組合的磁場
        for i in range(len(number_sequence) - 1):
            pair = number_sequence[i:i+2]  # 取相鄰兩個數字
            for field_name, field_info in self.field_types.items():
                for pattern in field_info.get("patterns", []):
                    if "sequence" in pattern and pattern["sequence"] == pair:
                        fields[field_name] += pattern.get("value", 1)

        return fields

    def get_neutralization_strategy(self, fields):
        """根據當前磁場分佈，計算中和策略

        參數:
            fields: 當前磁場分佈

        返回:
            需要的正面磁場數量
        """
        # 初始化需要的正面磁場
        required_fields = {
            "伏位": 0, "生氣": 0, "天醫": 0, "延年": 0
        }

        # 天醫欺絕命：一個天醫對應一個絕命
        required_fields["天醫"] += fields.get("絕命", 0)

        # 延年壓六煞：一個延年對應一個六煞
        required_fields["延年"] += fields.get("六煞", 0)

        # 化解禍害
        # 策略：優先使用生氣+生氣，次之用生氣+延年，最後用生氣+伏位
        huo_hai = fields.get("禍害", 0)
        if huo_hai > 0:
            # 分配生氣
            required_fields["生氣"] += huo_hai
            # 假設一半的禍害用生氣+生氣，一半用生氣+伏位
            required_fields["伏位"] += huo_hai // 2  # 整除，取整數部分
            required_fields["生氣"] += huo_hai // 2  # 額外生氣

        # 化解五鬼：需要生氣+天醫+延年的組合
        wu_gui = fields.get("五鬼", 0)
        if wu_gui > 0:
            required_fields["生氣"] += wu_gui
            required_fields["天醫"] += wu_gui
            required_fields["延年"] += wu_gui

        return required_fields

    # def analyze_compatibility(self, number_sequence):
        """分析數字序列的能量相容性

        參數:
            number_sequence: 數字序列

        返回:
            相容性分析結果
        """
        # 計算磁場分佈
        fields = self.get_number_fields(number_sequence)

        # 計算正面和負面磁場總數
        positive_count = sum(fields[f] for f in ["伏位", "生氣", "天醫", "延年"])  # 正面磁場總數
        negative_count = sum(fields[f] for f in ["絕命", "禍害", "五鬼", "六煞"])  # 負面磁場總數

        # 計算能量平衡度分數 (0-100)
        if positive_count + negative_count == 0:
            balance_score = 50  # 中性
        else:
            balance_score = min(100, int(positive_count / (positive_count + negative_count) * 100))

        return {
            "fields": fields,  # 各磁場數量
            "positive_count": positive_count,  # 正面磁場總數
            "negative_count": negative_count,  # 負面磁場總數
            "balance_score": balance_score,    # 平衡度分數
            "interpretation": self._generate_compatibility_interpretation(fields, balance_score)  # 解釋文字
        }

    # def _generate_compatibility_interpretation(self, fields, balance_score):
        """生成能量相容性的解釋文字

        參數:
            fields: 磁場分佈
            balance_score: 平衡度分數

        返回:
            解釋文字
        """
        interpretation = []

        # 根據平衡度給出總體評價
        if balance_score >= 80:
            interpretation.append("這組數字具有極佳的能量平衡，正面磁場顯著高於負面磁場。")
        elif balance_score >= 60:
            interpretation.append("這組數字能量較為平衡，正面磁場略高於負面磁場。")
        elif balance_score >= 40:
            interpretation.append("這組數字能量中性，正面與負面磁場大致平衡。")
        elif balance_score >= 20:
            interpretation.append("這組數字負面能量較強，建議尋找更平衡的組合。")
        else:
            interpretation.append("這組數字負面能量顯著，強烈建議尋找更合適的組合。")

        # 分析主要的磁場
        strongest_fields = []
        for field, count in fields.items():
            if count > 0:
                strongest_fields.append((field, count))

        # 按磁場數量排序
        strongest_fields.sort(key=lambda x: x[1], reverse=True)

        if strongest_fields:
            top_fields = strongest_fields[:3]  # 取前三強的磁場
            field_descriptions = []

            for field, count in top_fields:
                if count > 0:
                    # 顯示磁場類型和數量
                    energy_type = "正面" if self.is_positive_field(field) else "負面"
                    field_descriptions.append(f"{field}({count}個，{energy_type}能量)")

            if field_descriptions:
                interpretation.append(f"主要磁場: {', '.join(field_descriptions)}。")

        # 提供改善建議
        if balance_score < 60:
            # 計算化解策略
            strategy = self.get_neutralization_strategy(fields)
            suggestions = []

            for field, count in strategy.items():
                if count > 0:
                    suggestions.append(f"{field} {count}個")

            if suggestions:
                interpretation.append(f"建議增加以下正面磁場以改善能量平衡: {', '.join(suggestions)}。")

        return " ".join(interpretation)



