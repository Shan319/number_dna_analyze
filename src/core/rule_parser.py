#  core/rule_parser.py
"""
[Deprecate] 數字 DNA 分析器 - 規則解析器
負責解析和處理規則檔案，為分析引擎提供結構化規則數據。

功能：
1. 解析基本數字能量規則文件(base_rules.json)
2. 解析八大磁場計算規則文件(field_rules.json)
3. 驗證規則的有效性
4. 提供規則查詢和應用機制
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set, Optional

from src.utils import main_service
# 設定日誌記錄器


class RuleParser:
    """規則解析與處理類"""

    def __init__(self, rules_directory: str | None = None):
        """
        初始化規則解析器

        Args:
            rules_directory (str): 規則檔案目錄，如果未提供則使用預設路徑
        """
        self.logger = main_service.log.get_logger("數字 DNA 分析器.RuleParser")

        # 設定規則目錄
        if rules_directory is None:
            base_dir = Path(__file__).parent.parent
            self.rules_directory: str = os.path.join(base_dir, "resources", "rules")
        else:
            self.rules_directory = rules_directory

        self.logger.info(f"初始化規則解析器，規則目錄: {self.rules_directory}")

        # 初始化規則存儲
        self.base_rules = {}
        self.field_rules = {}
        self.magnetic_pairs = {}
        self.magnetic_properties = {}
        self.rule_cancellations = {}

        # 載入規則
        self._load_rules()

    def _load_rules(self) -> None:
        """載入所有規則文件"""
        try:
            # 載入基本規則
            base_rules_path = os.path.join(self.rules_directory, "base_rules.json")
            if os.path.exists(base_rules_path):
                self.base_rules = self._load_json_file(base_rules_path)
                self.logger.info("已載入基本數字能量規則")
            else:
                self.logger.warning(f"基本規則檔案不存在: {base_rules_path}")

            # 載入磁場規則
            field_rules_path = os.path.join(self.rules_directory, "field_rules.json")
            if os.path.exists(field_rules_path):
                self.field_rules = self._load_json_file(field_rules_path)
                self.logger.info("已載入八大磁場計算規則")
            else:
                self.logger.warning(f"磁場規則檔案不存在: {field_rules_path}")

            # 解析規則
            self._parse_rules()

        except Exception as e:
            self.logger.error(f"載入規則失敗: {e}", exc_info=True)
            raise RuntimeError(f"無法載入規則檔案: {e}")

    def _load_json_file(self, file_path: str) -> Dict:
        """
        載入JSON文件

        Args:
            file_path (str): JSON文件路徑

        Returns:
            Dict: 解析後的JSON數據
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析錯誤 ({file_path}): {e}")
            raise
        except Exception as e:
            self.logger.error(f"載入文件失敗 ({file_path}): {e}")
            raise

    def _parse_rules(self) -> None:
        """解析載入的規則數據"""
        # 解析磁場對應的數字組合
        self._parse_magnetic_pairs()

        # 解析磁場屬性
        self._parse_magnetic_properties()

        # 解析規則抵消關係
        self._parse_rule_cancellations()

    def _parse_magnetic_pairs(self) -> None:
        """解析磁場對應的數字組合"""
        try:
            if 'magnetic_pairs' in self.field_rules:
                self.magnetic_pairs = self.field_rules['magnetic_pairs']
                self.logger.debug(f"解析磁場對應數字組合: {len(self.magnetic_pairs)} 組")
            else:
                # 如果規則文件中沒有，使用預設值
                self.magnetic_pairs = {
                    "伏位": ["00", "11", "22", "33", "44", "66", "77", "88", "99"],
                    "延年": ["19", "91", "78", "87", "43", "34", "26", "62"],
                    "生氣": ["14", "41", "67", "76", "93", "39", "28", "82"],
                    "天醫": ["13", "31", "68", "86", "94", "49", "72", "27"],
                    "六煞": ["16", "61", "74", "47", "38", "83", "92", "29"],
                    "絕命": ["12", "21", "69", "96", "84", "48", "37", "73"],
                    "禍害": ["17", "71", "98", "89", "64", "46", "32", "23"],
                    "五鬼": ["18", "81", "97", "79", "36", "63", "42", "24"]
                }
                self.logger.info("使用預設磁場對應數字組合")

            # 生成反向查找表以提高查詢效率
            self.pair_to_field = {}
            for field, pairs in self.magnetic_pairs.items():
                for pair in pairs:
                    self.pair_to_field[pair] = field
        except Exception as e:
            self.logger.error(f"解析磁場對應數字組合失敗: {e}", exc_info=True)
            raise

    def _parse_magnetic_properties(self) -> None:
        """解析磁場屬性（關鍵字、優缺點等）"""
        try:
            if 'magnetic_fields' in self.field_rules:
                self.magnetic_properties = self.field_rules['magnetic_fields']
                self.logger.debug(f"解析磁場屬性: {len(self.magnetic_properties)} 組")
            else:
                # 如果規則文件中沒有，使用預設值
                self.magnetic_properties = {
                    "伏位": {
                        "keywords": ["蓄勢待發", "狀況延續", "臥虎藏龍"],
                        "strengths": "有耐心、責任心強、幽默風趣、善於溝通協調",
                        "weaknesses": "矛盾交錯、沒有安全感、主觀意識強、作風保守",
                        "financial_strategy": "耐心積累，穩健投資，適合選擇風險較低、回報穩定的金融產品",
                        "relationship_advice": "尋求穩定與安全感，在互動中需要耐心溝通"
                    },
                    "生氣": {
                        "keywords": ["貴人", "轉機", "好名聲"],
                        "strengths": "樂天派、凡事不強求、熱心助人、擁有好人緣",
                        "weaknesses": "企圖心不旺盛，由於對任何事不強求隨遇而安",
                        "financial_strategy": "積極開拓，慎選機遇，避免盲目跟風",
                        "relationship_advice": "積極互動，珍惜緣分，避免過度追求新鮮感"
                    },
                    "天醫": {
                        "keywords": ["主大才", "天生聰穎", "文筆好"],
                        "strengths": "賺錢有如神助、諸事順遂、外型氣質俱佳",
                        "weaknesses": "極度善良，偶爾會被蒙騙",
                        "financial_strategy": "智慧投資，行善積福，防範詐騙",
                        "relationship_advice": "關懷對方，共同成長，給予情感支持"
                    },
                    "延年": {
                        "keywords": ["意志堅定的領袖格局"],
                        "strengths": "決斷力強、內斂成熟",
                        "weaknesses": "缺少彈性變通，做事強勢，一板一眼",
                        "financial_strategy": "領導風範，規劃未來，長期財務規劃",
                        "relationship_advice": "領導與支持，平衡關係，聆聽對方意見"
                    },
                    "絕命": {
                        "keywords": ["高IQ低EQ", "大起大落的極端特質"],
                        "strengths": "反應靈敏、善於謀略，重視精神層面",
                        "weaknesses": "缺乏圓融、執著己見",
                        "financial_strategy": "冷靜應對，規避風險，避免情緒化決策",
                        "relationship_advice": "情緒管理，避免極端，冷靜處理糾紛"
                    },
                    "禍害": {
                        "keywords": ["口舌", "病弱", "心機"],
                        "strengths": "辯才無礙、能言善道",
                        "weaknesses": "口舌之爭不斷、身體狀況不佳",
                        "financial_strategy": "口才服人，謹慎決策，避免過度自信",
                        "relationship_advice": "慎選言辭，避免衝突，注意言辭影響"
                    },
                    "五鬼": {
                        "keywords": ["最有才華但最不穩定", "際遇波折"],
                        "strengths": "鬼才洋溢、快速的學習力",
                        "weaknesses": "變動太快，難以產生安定力量",
                        "financial_strategy": "創新思維，謹慎投資，避免忽視風險",
                        "relationship_advice": "創新互動，忠誠為本，保持透明度"
                    },
                    "六煞": {
                        "keywords": ["情感", "婚姻", "或人際關係方面糾葛"],
                        "strengths": "異性緣特別好、具有俊男美女的外貌",
                        "weaknesses": "總是為情所困，感情、事業、工作不順遂",
                        "financial_strategy": "和諧人際，謹慎合作，明確權責界限",
                        "relationship_advice": "和諧相處，避免糾纏，設定清晰界限"
                    }
                }
                self.logger.info("使用預設磁場屬性")
        except Exception as e:
            self.logger.error(f"解析磁場屬性失敗: {e}", exc_info=True)
            raise

    def _parse_rule_cancellations(self) -> None:
        """解析規則抵消關係"""
        try:
            if 'rule_cancellations' in self.field_rules:
                self.rule_cancellations = self.field_rules['rule_cancellations']
                self.logger.debug(f"解析規則抵消關係: {len(self.rule_cancellations)} 組")
            else:
                # 如果規則文件中沒有，使用預設值
                self.rule_cancellations = {
                    "天醫_絕命": {
                        "description": "天醫可抵消絕命",
                        "ratio": 1
                    },
                    "延年_六煞": {
                        "description": "延年可抵消六煞",
                        "ratio": 1
                    },
                    "生氣伏位_禍害": {
                        "description": "生氣和伏位的組合可抵消禍害",
                        "ratio": 1
                    },
                    "天醫延年_禍害": {
                        "description": "天醫和延年的組合可抵消禍害",
                        "ratio": 1
                    },
                    "生氣天醫延年_五鬼": {
                        "description": "生氣、天醫和延年的組合可抵消五鬼",
                        "ratio": 1
                    }
                }
                self.logger.info("使用預設規則抵消關係")
        except Exception as e:
            self.logger.error(f"解析規則抵消關係失敗: {e}", exc_info=True)
            raise

    def get_field_from_pair(self, pair: str) -> str:
        """
        根據數字對取得對應的磁場名稱

        Args:
            pair (str): 二位數字對，如 "13"

        Returns:
            str: 磁場名稱，如 "天醫"
        """
        return self.pair_to_field.get(pair, "未知")

    def get_all_magnetic_fields(self) -> List[str]:
        """
        取得所有磁場名稱列表

        Returns:
            List[str]: 磁場名稱列表
        """
        return list(self.magnetic_pairs.keys())

    def get_magnetic_properties(self, field_name: str) -> Dict:
        """
        獲取指定磁場的屬性

        Args:
            field_name (str): 磁場名稱

        Returns:
            Dict: 磁場屬性字典
        """
        return self.magnetic_properties.get(field_name, {})

    def get_cancellation_rules(self) -> Dict:
        """
        獲取規則抵消關係

        Returns:
            Dict: 規則抵消關係字典
        """
        return self.rule_cancellations

    def transform_numbers_to_fields(self, number_sequence: str) -> List[str]:
        """
        將數字序列轉換為磁場序列

        Args:
            number_sequence (str): 數字序列

        Returns:
            List[str]: 磁場名稱列表
        """

        # 實現數字轉換規則
        def handle_5_between_9_1(s):
            """處理9-5-1和1-5-9的特殊情況"""
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

        # 處理特殊組合
        processed_number = handle_5_between_9_1(number_sequence)

        # 處理中間的5
        if len(processed_number) > 2:
            processed_number = processed_number[0] + processed_number[1:-1].replace(
                '5', '') + processed_number[-1]

        # 處理首尾的5
        if len(processed_number) >= 2:
            if processed_number[0] == '5':
                processed_number = processed_number[1] * 2 + processed_number[1:]
            if processed_number[-1] == '5':
                processed_number = processed_number[:-2] + processed_number[-2] * 2

        # 生成數字對
        pairs = []
        for i in range(len(processed_number) - 1):
            a, b = processed_number[i], processed_number[i + 1]
            if (a == '0' and b != '5') or (b == '0' and a != '5'):
                pair = b * 2 if a == '0' else a * 2
            elif (a == '5' and b == '0') or (a == '0' and b == '5'):
                pair = "00"
            elif a == '5' or b == '5':
                pair = b * 2 if a == '5' else a * 2
            else:
                pair = a + b
            pairs.append(pair)

        # 將數字對轉換為磁場名稱
        fields = [self.get_field_from_pair(pair) for pair in pairs]

        return fields

    def apply_advanced_rules(self, fields: List[str]) -> Tuple[Dict[str, int], List[str]]:
        """
        應用進階規則處理磁場序列

        Args:
            fields (List[str]): 磁場名稱列表

        Returns:
            Tuple[Dict[str, int], List[str]]: (調整後的計數字典, 調整日誌)
        """
        from collections import Counter

        # 初步計數
        base_counts = Counter(fields)
        adjusted_counts = base_counts.copy()
        adjust_log = []

        # 使用set來記錄已使用的索引
        used_indexes = set()

        # 規則 1：天醫 vs 絕命 抵銷
        cancel_count = min(adjusted_counts["天醫"], adjusted_counts["絕命"])
        if cancel_count > 0:
            adjusted_counts["天醫"] -= cancel_count
            adjusted_counts["絕命"] -= cancel_count
            adjust_log.append(f"(天醫-{cancel_count})")
            adjust_log.append(f"(絕命-{cancel_count})")

        # 規則 2：延年 vs 六煞 抵銷
        cancel_count = min(adjusted_counts["延年"], adjusted_counts["六煞"])
        if cancel_count > 0:
            adjusted_counts["延年"] -= cancel_count
            adjusted_counts["六煞"] -= cancel_count
            adjust_log.append(f"(延年-{cancel_count})")
            adjust_log.append(f"(六煞-{cancel_count})")

        # 規則 3：固定對組合 -> 抵一個禍害
        group_pairs = [("生氣", "生氣"), ("生氣", "延年"), ("生氣", "伏位"), ("延年", "生氣")]
        i = 0
        while i < len(fields) - 1:
            pair = (fields[i], fields[i + 1])
            if pair in group_pairs and adjusted_counts["禍害"] > 0:
                adjust_log.append(f"({pair[0]}-1) ({pair[1]}-1) (禍害-1)")
                adjusted_counts[pair[0]] -= 1
                adjusted_counts[pair[1]] -= 1
                adjusted_counts["禍害"] -= 1
                used_indexes.update([i, i + 1])
                i += 2
            else:
                i += 1

        # 規則 4：生氣+天醫+延年 -> 抵五鬼
        i = 0
        while i < len(fields) - 2:
            triplet = fields[i:i + 3]
            if triplet == ["生氣", "天醫", "延年"] and adjusted_counts["五鬼"] > 0:
                adjust_log.append("(生氣-1) (天醫-1) (延年-1) (五鬼-1)")
                for t in triplet:
                    adjusted_counts[t] -= 1
                adjusted_counts["五鬼"] -= 1
                i += 3
            else:
                i += 1

        # 規則 5：磁場後連續伏位，需排除已使用 index
        i = 0
        while i < len(fields) - 1:
            if i in used_indexes or fields[i] == "伏位":
                i += 1
                continue

            count = 0
            j = i + 1
            while j < len(fields) and fields[j] == "伏位" and j not in used_indexes:
                count += 1
                j += 1

            if count > 0 and adjusted_counts["伏位"] >= count:
                adjusted_counts[fields[i]] += count
                adjusted_counts["伏位"] -= count
                adjust_log.append(f"({fields[i]}+{count}) (伏位-{count})")
                for k in range(i, j):
                    used_indexes.add(k)
                i = j
            else:
                i += 1

        # 移除計數為0的項目
        adjusted_counts = {k: v for k, v in adjusted_counts.items() if v > 0}

        return adjusted_counts, adjust_log

    def validate_rules(self) -> bool:
        """
        驗證規則的有效性和完整性

        Returns:
            bool: 規則是否有效
        """
        # 檢查必需的磁場是否都存在
        required_fields = ["伏位", "延年", "生氣", "天醫", "六煞", "絕命", "禍害", "五鬼"]
        for field in required_fields:
            if field not in self.magnetic_pairs:
                self.logger.error(f"缺少必需的磁場定義: {field}")
                return False

        # 檢查每個磁場是否都有對應的數字組合
        for field in self.magnetic_pairs:
            if not self.magnetic_pairs[field]:
                self.logger.error(f"磁場 {field} 沒有對應的數字組合")
                return False

        # 檢查所有數字對是否都有唯一對應的磁場
        all_pairs = set()
        for field, pairs in self.magnetic_pairs.items():
            for pair in pairs:
                if pair in all_pairs:
                    self.logger.error(f"數字對 {pair} 在多個磁場中重複定義")
                    return False
                all_pairs.add(pair)

        return True


# 如果直接執行此模組，運行測試
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = RuleParser()

    # 測試轉換
    test_number = "13579"
    fields = parser.transform_numbers_to_fields(test_number)
    print(f"數字 {test_number} 轉換為磁場: {fields}")

    # 測試應用規則
    adjusted, log = parser.apply_advanced_rules(fields)
    print(f"調整後: {adjusted}")
    print(f"調整日誌: {log}")

    # 測試獲取磁場屬性
    for field in parser.get_all_magnetic_fields():
        props = parser.get_magnetic_properties(field)
        print(f"{field}: {props.get('keywords', [])}")
