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
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import shutil

# 如果可用，導入模型定義
try:
    from data.models import MagneticField, MagneticPair, RuleModel
    models_available = True
except ImportError:
    models_available = False

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.RuleRepository")

class RuleRepository:
    """規則庫類，管理磁場分析規則"""

    def __init__(self, file_manager=None, rules_dir: str = None):
        """
        初始化規則庫

        Args:
            file_manager: 檔案管理器實例
            rules_dir (str): 規則檔案目錄，如果為None則使用預設路徑
        """
        self.logger = logging.getLogger("數字DNA分析器.RuleRepository")

        # 儲存檔案管理器
        self.file_manager = file_manager

        # 設定規則目錄
        if rules_dir is None:
            base_dir = Path(__file__).parent.parent
            self.rules_dir = os.path.join(base_dir, "resources", "rules")
        else:
            self.rules_dir = rules_dir

        # 確保目錄存在
        os.makedirs(self.rules_dir, exist_ok=True)

        # 初始化規則快取
        self.rules_cache = {}
        self.last_update_time = {}

        # 常用規則檔案路徑
        self.base_rules_path = os.path.join(self.rules_dir, "base_rules.json")
        self.field_rules_path = os.path.join(self.rules_dir, "field_rules.json")

        # 檢查是否需要初始化
        self._check_and_initialize_rules()

        self.logger.info(f"規則庫初始化完成，規則目錄: {self.rules_dir}")

    def _check_and_initialize_rules(self):
        """檢查並初始化規則檔案"""
        # 檢查基本規則檔案
        if not os.path.exists(self.base_rules_path):
            self.logger.warning(f"基本規則檔案不存在: {self.base_rules_path}")
            self._initialize_base_rules()

        # 檢查磁場規則檔案
        if not os.path.exists(self.field_rules_path):
            self.logger.warning(f"磁場規則檔案不存在: {self.field_rules_path}")
            self._initialize_field_rules()

    def _initialize_base_rules(self):
        """初始化基本規則檔案"""
        default_base_rules = {
            "version": "1.0.0",
            "last_updated": time.time(),
            "energy_numbers": {
                "1": {
                    "name": "太陽數",
                    "description": "領導力、自信、創造力",
                    "positive": "領導能力、創新思維、積極主動",
                    "negative": "自我中心、固執、傲慢",
                    "career": "管理職位、創意工作、自主創業",
                    "relationships": "喜歡主導關係，需要有耐心的伴侶"
                },
                "2": {
                    "name": "月亮數",
                    "description": "和諧、平衡、敏感",
                    "positive": "善解人意、協調能力、直覺敏銳",
                    "negative": "過度敏感、優柔寡斷、情緒波動",
                    "career": "輔導、外交、團隊合作",
                    "relationships": "善於聆聽，珍視情感連結"
                },
                "3": {
                    "name": "木星數",
                    "description": "表達、樂觀、創意",
                    "positive": "溝通能力強、熱情開朗、創意豐富",
                    "negative": "表面化、缺乏耐心、三分鐘熱度",
                    "career": "藝術、媒體、銷售",
                    "relationships": "善於表達感情，樂於分享"
                },
                "4": {
                    "name": "天王星數",
                    "description": "穩定、務實、耐心",
                    "positive": "踏實可靠、條理分明、堅持不懈",
                    "negative": "固執保守、缺乏變通、過度拘泥",
                    "career": "工程、財務、規劃",
                    "relationships": "忠誠可靠，重視承諾"
                },
                "5": {
                    "name": "水星數",
                    "description": "自由、變化、冒險",
                    "positive": "適應力強、好奇心重、喜歡探索",
                    "negative": "缺乏恆心、不安分、衝動",
                    "career": "旅遊、行銷、自由職業",
                    "relationships": "需要空間與自由，不喜被束縛"
                },
                "6": {
                    "name": "金星數",
                    "description": "愛、和諧、責任",
                    "positive": "關愛他人、審美能力強、責任感強",
                    "negative": "過度犧牲、完美主義、過度操心",
                    "career": "設計、諮詢、服務業",
                    "relationships": "重視家庭和諧，願意付出"
                },
                "7": {
                    "name": "海王星數",
                    "description": "精神、智慧、分析",
                    "positive": "思考深刻、直覺敏銳、追求知識",
                    "negative": "過度分析、懷疑主義、不切實際",
                    "career": "研究、寫作、心靈工作",
                    "relationships": "重視精神連結，內斂含蓄"
                },
                "8": {
                    "name": "土星數",
                    "description": "權力、成就、物質",
                    "positive": "組織能力強、權威性、商業頭腦",
                    "negative": "工作狂、控制慾強、物質主義",
                    "career": "企業管理、金融、投資",
                    "relationships": "追求穩定，提供安全感"
                },
                "9": {
                    "name": "火星數",
                    "description": "完成、智慧、人道",
                    "positive": "同理心強、博愛精神、智慧成熟",
                    "negative": "不切實際、不合群、沉溺過去",
                    "career": "教育、公益、心理諮詢",
                    "relationships": "富有同情心，追求理想關係"
                }
            },
            "number_combinations": {
                "11": {"name": "高靈數", "description": "精神啟發、直覺、靈性"},
                "22": {"name": "大師數", "description": "實現夢想、建設者、領導者"},
                "33": {"name": "教師數", "description": "慈悲、教導、奉獻"}
            }
        }

        try:
            # 儲存預設規則
            with open(self.base_rules_path, 'w', encoding='utf-8') as f:
                json.dump(default_base_rules, f, ensure_ascii=False, indent=4)

            self.logger.info(f"已創建預設基本規則檔案: {self.base_rules_path}")
        except Exception as e:
            self.logger.error(f"創建預設基本規則檔案失敗: {e}")

    def _initialize_field_rules(self):
        """初始化磁場規則檔案"""
        default_field_rules = {
            "version": "1.0.0",
            "last_updated": time.time(),
            "magnetic_pairs": {
                "伏位": ["00", "11", "22", "33", "44", "66", "77", "88", "99"],
                "延年": ["19", "91", "78", "87", "43", "34", "26", "62"],
                "生氣": ["14", "41", "67", "76", "93", "39", "28", "82"],
                "天醫": ["13", "31", "68", "86", "94", "49", "72", "27"],
                "六煞": ["16", "61", "74", "47", "38", "83", "92", "29"],
                "絕命": ["12", "21", "69", "96", "84", "48", "37", "73"],
                "禍害": ["17", "71", "98", "89", "64", "46", "32", "23"],
                "五鬼": ["18", "81", "97", "79", "36", "63", "42", "24"]
            },
            "magnetic_fields": {
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
            },
            "rule_cancellations": {
                "天醫_絕命": {"description": "天醫可抵消絕命", "ratio": 1},
                "延年_六煞": {"description": "延年可抵消六煞", "ratio": 1},
                "生氣伏位_禍害": {"description": "生氣和伏位的組合可抵消禍害", "ratio": 1},
                "天醫延年_禍害": {"description": "天醫和延年的組合可抵消禍害", "ratio": 1},
                "生氣天醫延年_五鬼": {"description": "生氣、天醫和延年的組合可抵消五鬼", "ratio": 1}
            },
            "transform_rules": {
                "number_5": {
                    "start": "後面數字的兩倍",
                    "end": "前面數字的兩倍",
                    "middle": "移除",
                    "special_9_5_1": "變成9191"
                },
                "number_0": {
                    "with_5": "變成00",
                    "with_others": "另一個數字的兩倍"
                }
            }
        }

        try:
            # 儲存預設規則
            with open(self.field_rules_path, 'w', encoding='utf-8') as f:
                json.dump(default_field_rules, f, ensure_ascii=False, indent=4)

            self.logger.info(f"已創建預設磁場規則檔案: {self.field_rules_path}")
        except Exception as e:
            self.logger.error(f"創建預設磁場規則檔案失敗: {e}")

    def _load_rule_file(self, file_path: str) -> Dict[str, Any]:
        """
        載入規則檔案

        Args:
            file_path (str): 規則檔案路徑

        Returns:
            Dict[str, Any]: 規則數據
        """
        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            self.logger.warning(f"規則檔案不存在: {file_path}")
            return {}

        # 檢查檔案是否已載入且未修改
        file_mtime = os.path.getmtime(file_path)
        if file_path in self.rules_cache and file_mtime <= self.last_update_time.get(file_path, 0):
            return self.rules_cache[file_path]

        try:
            # 使用檔案管理器載入（如果可用）
            if self.file_manager and hasattr(self.file_manager, 'load_resource_json'):
                # 計算相對路徑
                rel_path = os.path.relpath(file_path, self.file_manager.resources_dir)
                rules = self.file_manager.load_resource_json(rel_path)
            else:
                # 直接讀取檔案
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)

            # 更新快取
            self.rules_cache[file_path] = rules
            self.last_update_time[file_path] = file_mtime

            self.logger.debug(f"成功載入規則檔案: {file_path}")
            return rules
        except json.JSONDecodeError:
            self.logger.error(f"規則檔案格式錯誤: {file_path}")
            return {}
        except Exception as e:
            self.logger.error(f"載入規則檔案失敗: {file_path}, 錯誤: {e}")
            return {}

    def _save_rule_file(self, file_path: str, rules: Dict[str, Any]) -> bool:
        """
        儲存規則檔案

        Args:
            file_path (str): 規則檔案路徑
            rules (Dict[str, Any]): 規則數據

        Returns:
            bool: 儲存是否成功
        """
        try:
            # 更新時間戳
            rules["last_updated"] = time.time()

            # 使用檔案管理器儲存（如果可用）
            if self.file_manager and hasattr(self.file_manager, 'save_resource_json'):
                # 計算相對路徑
                rel_path = os.path.relpath(file_path, self.file_manager.resources_dir)
                success = self.file_manager.save_resource_json(rel_path, rules)
            else:
                # 備份現有檔案（如果存在）
                if os.path.exists(file_path):
                    backup_path = f"{file_path}.bak"
                    shutil.copy2(file_path, backup_path)

                # 直接寫入檔案
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, ensure_ascii=False, indent=4)
                success = True

            if success:
                # 更新快取
                self.rules_cache[file_path] = rules
                self.last_update_time[file_path] = time.time()

            self.logger.debug(f"成功儲存規則檔案: {file_path}")
            return success
        except Exception as e:
            self.logger.error(f"儲存規則檔案失敗: {file_path}, 錯誤: {e}")
            return False

    def load_base_rules(self) -> Dict[str, Any]:
        """
        載入基本規則

        Returns:
            Dict[str, Any]: 基本規則數據
        """
        return self._load_rule_file(self.base_rules_path)

    def load_field_rules(self) -> Dict[str, Any]:
        """
        載入磁場規則

        Returns:
            Dict[str, Any]: 磁場規則數據
        """
        return self._load_rule_file(self.field_rules_path)

    def load_rules(self) -> Dict[str, Any]:
        """
        載入所有規則

        Returns:
            Dict[str, Any]: 所有規則數據
        """
        base_rules = self.load_base_rules()
        field_rules = self.load_field_rules()

        # 合併規則
        rules = {
            "base_rules": base_rules,
            "field_rules": field_rules
        }

        return rules

    def update_base_rules(self, rules: Dict[str, Any]) -> bool:
        """
        更新基本規則

        Args:
            rules (Dict[str, Any]): 基本規則數據

        Returns:
            bool: 更新是否成功
        """
        # 確保版本號
        if "version" not in rules:
            rules["version"] = "1.0.0"

        return self._save_rule_file(self.base_rules_path, rules)

    def update_field_rules(self, rules: Dict[str, Any]) -> bool:
        """
        更新磁場規則

        Args:
            rules (Dict[str, Any]): 磁場規則數據

        Returns:
            bool: 更新是否成功
        """
        # 確保版本號
        if "version" not in rules:
            rules["version"] = "1.0.0"

        return self._save_rule_file(self.field_rules_path, rules)

    def get_magnetic_pairs(self) -> Dict[str, List[str]]:
        """
        獲取磁場對應的數字對

        Returns:
            Dict[str, List[str]]: 磁場對應的數字對
        """
        field_rules = self.load_field_rules()
        return field_rules.get("magnetic_pairs", {})

    def get_magnetic_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取磁場屬性

        Returns:
            Dict[str, Dict[str, Any]]: 磁場屬性
        """
        field_rules = self.load_field_rules()
        return field_rules.get("magnetic_fields", {})

    def get_rule_cancellations(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取規則抵消關係

        Returns:
            Dict[str, Dict[str, Any]]: 規則抵消關係
        """
        field_rules = self.load_field_rules()
        return field_rules.get("rule_cancellations", {})

    def get_transform_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取數字轉換規則

        Returns:
            Dict[str, Dict[str, Any]]: 數字轉換規則
        """
        field_rules = self.load_field_rules()
        return field_rules.get("transform_rules", {})

    def get_energy_numbers(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取數字能量屬性

        Returns:
            Dict[str, Dict[str, Any]]: 數字能量屬性
        """
        base_rules = self.load_base_rules()
        return base_rules.get("energy_numbers", {})

    def get_number_combinations(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取數字組合屬性

        Returns:
            Dict[str, Dict[str, Any]]: 數字組合屬性
        """
        base_rules = self.load_base_rules()
        return base_rules.get("number_combinations", {})

    def get_field_by_pair(self, pair: str) -> str:
        """
        根據數字對獲取對應的磁場

        Args:
            pair (str): 數字對，如 "13"

        Returns:
            str: 磁場名稱，如 "天醫"
        """
        magnetic_pairs = self.get_magnetic_pairs()

        for field, pairs in magnetic_pairs.items():
            if pair in pairs:
                return field

        return "未知"

    def get_field_attributes(self, field_name: str) -> Dict[str, Any]:
        """
        獲取磁場的屬性

        Args:
            field_name (str): 磁場名稱

        Returns:
            Dict[str, Any]: 磁場屬性
        """
        magnetic_fields = self.get_magnetic_fields()
        return magnetic_fields.get(field_name, {})

    def get_base_rule_version(self) -> str:
        """
        獲取基本規則版本

        Returns:
            str: 版本號
        """
        base_rules = self.load_base_rules()
        return base_rules.get("version", "unknown")

    def get_field_rule_version(self) -> str:
        """
        獲取磁場規則版本

        Returns:
            str: 版本號
        """
        field_rules = self.load_field_rules()
        return field_rules.get("version", "unknown")

    def import_rules(self, file_path: str) -> bool:
        """
        從檔案匯入規則

        Args:
            file_path (str): 規則檔案路徑

        Returns:
            bool: 匯入是否成功
        """
        try:
            # 讀取檔案
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 檢查規則類型
            if "energy_numbers" in data:
                # 是基本規則
                return self.update_base_rules(data)
            elif "magnetic_pairs" in data:
                # 是磁場規則
                return self.update_field_rules(data)
            else:
                self.logger.warning(f"未知的規則類型: {file_path}")
                return False
        except json.JSONDecodeError:
            self.logger.error(f"規則檔案格式錯誤: {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"匯入規則失敗: {file_path}, 錯誤: {e}")
            return False

    def export_rules(self, file_path: str, rule_type: str = "all") -> bool:
        """
        匯出規則到檔案

        Args:
            file_path (str): 規則檔案路徑
            rule_type (str): 規則類型，可以是 "all", "base", "field"

        Returns:
            bool: 匯出是否成功
        """
        try:
            if rule_type == "base" or rule_type == "all":
                base_rules = self.load_base_rules()

                if rule_type == "base":
                    # 匯出基本規則
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(base_rules, f, ensure_ascii=False, indent=4)

                    self.logger.debug(f"成功匯出基本規則: {file_path}")
                    return True

            if rule_type == "field" or rule_type == "all":
                field_rules = self.load_field_rules()

                if rule_type == "field":
                    # 匯出磁場規則
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(field_rules, f, ensure_ascii=False, indent=4)

                    self.logger.debug(f"成功匯出磁場規則: {file_path}")
                    return True

            if rule_type == "all":
                # 匯出所有規則
                all_rules = {
                    "base_rules": base_rules,
                    "field_rules": field_rules
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_rules, f, ensure_ascii=False, indent=4)

                self.logger.debug(f"成功匯出所有規則: {file_path}")
                return True

            self.logger.warning(f"未知的規則類型: {rule_type}")
            return False
        except Exception as e:
            self.logger.error(f"匯出規則失敗: {file_path}, 錯誤: {e}")
            return False

    def reset_to_default(self, rule_type: str = "all") -> bool:
        """
        重置規則為預設值

        Args:
            rule_type (str): 規則類型，可以是 "all", "base", "field"

        Returns:
            bool: 重置是否成功
        """
        success = True

        if rule_type in ["base", "all"]:
            # 刪除基本規則檔案
            if os.path.exists(self.base_rules_path):
                os.remove(self.base_rules_path)

            # 初始化基本規則
            self._initialize_base_rules()

            # 清除快取
            if self.base_rules_path in self.rules_cache:
                del self.rules_cache[self.base_rules_path]

            success = success and os.path.exists(self.base_rules_path)

        if rule_type in ["field", "all"]:
            # 刪除磁場規則檔案
            if os.path.exists(self.field_rules_path):
                os.remove(self.field_rules_path)

            # 初始化磁場規則
            self._initialize_field_rules()

            # 清除快取
            if self.field_rules_path in self.rules_cache:
                del self.rules_cache[self.field_rules_path]

            success = success and os.path.exists(self.field_rules_path)

        return success

    def validate_rules(self) -> Tuple[bool, List[str]]:
        """
        驗證規則是否有效

        Returns:
            Tuple[bool, List[str]]: (是否有效, 錯誤訊息列表)
        """
        errors = []

        # 載入規則
        base_rules = self.load_base_rules()
        field_rules = self.load_field_rules()

        # 檢查基本規則
        if not base_rules:
            errors.append("基本規則檔案不存在或為空")
        else:
            # 檢查必要欄位
            if "energy_numbers" not in base_rules:
                errors.append("基本規則缺少能量數字定義")
            elif not isinstance(base_rules["energy_numbers"], dict):
                errors.append("能量數字定義格式錯誤")

            if "number_combinations" not in base_rules:
                errors.append("基本規則缺少數字組合定義")
            elif not isinstance(base_rules["number_combinations"], dict):
                errors.append("數字組合定義格式錯誤")

        # 檢查磁場規則
        if not field_rules:
            errors.append("磁場規則檔案不存在或為空")
        else:
            # 檢查必要欄位
            if "magnetic_pairs" not in field_rules:
                errors.append("磁場規則缺少數字對應定義")
            elif not isinstance(field_rules["magnetic_pairs"], dict):
                errors.append("數字對應定義格式錯誤")

            if "magnetic_fields" not in field_rules:
                errors.append("磁場規則缺少磁場屬性定義")
            elif not isinstance(field_rules["magnetic_fields"], dict):
                errors.append("磁場屬性定義格式錯誤")

            # 檢查磁場完整性
            pairs = field_rules.get("magnetic_pairs", {})
            fields = field_rules.get("magnetic_fields", {})

            # 所有磁場都應該有對應的數字對
            for field in fields:
                if field not in pairs:
                    errors.append(f"磁場 {field} 缺少數字對應")

            # 所有數字對應都應該有磁場屬性
            for field in pairs:
                if field not in fields:
                    errors.append(f"數字對應 {field} 缺少磁場屬性")

            # 檢查數字對是否唯一
            all_pairs = set()
            for field, field_pairs in pairs.items():
                for pair in field_pairs:
                    if pair in all_pairs:
                        errors.append(f"數字對 {pair} 在多個磁場中出現")
                    all_pairs.add(pair)

        return len(errors) == 0, errors

    def update_field_attribute(self, field_name: str, attribute: str, value: Any) -> bool:
        """
        更新磁場屬性

        Args:
            field_name (str): 磁場名稱
            attribute (str): 屬性名稱
            value (Any): 屬性值

        Returns:
            bool: 更新是否成功
        """
        field_rules = self.load_field_rules()

        # 檢查磁場是否存在
        if "magnetic_fields" not in field_rules:
            field_rules["magnetic_fields"] = {}

        if field_name not in field_rules["magnetic_fields"]:
            field_rules["magnetic_fields"][field_name] = {}

        # 更新屬性
        field_rules["magnetic_fields"][field_name][attribute] = value

        # 儲存規則
        return self.update_field_rules(field_rules)

    def update_number_attribute(self, number: str, attribute: str, value: Any) -> bool:
        """
        更新數字能量屬性

        Args:
            number (str): 數字
            attribute (str): 屬性名稱
            value (Any): 屬性值

        Returns:
            bool: 更新是否成功
        """
        base_rules = self.load_base_rules()

        # 檢查數字是否存在
        if "energy_numbers" not in base_rules:
            base_rules["energy_numbers"] = {}

        if number not in base_rules["energy_numbers"]:
            base_rules["energy_numbers"][number] = {}

        # 更新屬性
        base_rules["energy_numbers"][number][attribute] = value

        # 儲存規則
        return self.update_base_rules(base_rules)

    def get_model_objects(self) -> Dict[str, List[Any]]:
        """
        獲取模型對象（如果models模組可用）

        Returns:
            Dict[str, List[Any]]: 模型對象字典
        """
        if not models_available:
            self.logger.warning("models模組不可用，無法創建模型對象")
            return {}

        result = {}

        try:
            # 載入規則
            magnetic_fields = self.get_magnetic_fields()
            magnetic_pairs = self.get_magnetic_pairs()

            # 創建磁場模型
            field_models = []
            for field_name, attributes in magnetic_fields.items():
                # 處理關鍵字
                keywords = attributes.get("keywords", [])
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split("、")]

                field_model = MagneticField(
                    name=field_name,
                    keywords=keywords,
                    strengths=attributes.get("strengths", ""),
                    weaknesses=attributes.get("weaknesses", ""),
                    financial_strategy=attributes.get("financial_strategy", ""),
                    relationship_advice=attributes.get("relationship_advice", "")
                )
                field_models.append(field_model)

            result["magnetic_fields"] = field_models

            # 創建磁場對模型
            pair_models = []
            for field_name, pairs in magnetic_pairs.items():
                pair_model = MagneticPair(
                    field=field_name,
                    number_pairs=pairs
                )
                pair_models.append(pair_model)

            result["magnetic_pairs"] = pair_models

            return result
        except Exception as e:
            self.logger.error(f"創建模型對象失敗: {e}")
            return {}

    def backup_rules(self, backup_dir: str = None) -> Tuple[bool, str]:
        """
        備份規則檔案

        Args:
            backup_dir (str): 備份目錄，如果為None則使用預設目錄

        Returns:
            Tuple[bool, str]: (是否成功, 備份目錄)
        """
        if backup_dir is None:
            # 使用時間戳創建備份目錄
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(self.rules_dir), "rules_backup", timestamp)

        try:
            # 確保備份目錄存在
            os.makedirs(backup_dir, exist_ok=True)

            # 備份基本規則
            if os.path.exists(self.base_rules_path):
                shutil.copy2(self.base_rules_path, os.path.join(backup_dir, os.path.basename(self.base_rules_path)))

            # 備份磁場規則
            if os.path.exists(self.field_rules_path):
                shutil.copy2(self.field_rules_path, os.path.join(backup_dir, os.path.basename(self.field_rules_path)))

            # 備份其他規則檔案
            for filename in os.listdir(self.rules_dir):
                if filename.endswith(".json") and filename not in [os.path.basename(self.base_rules_path), os.path.basename(self.field_rules_path)]:
                    src = os.path.join(self.rules_dir, filename)
                    dst = os.path.join(backup_dir, filename)
                    shutil.copy2(src, dst)

            self.logger.info(f"成功備份規則檔案到: {backup_dir}")
            return True, backup_dir
        except Exception as e:
            self.logger.error(f"備份規則檔案失敗: {e}")
            return False, ""

    def restore_rules(self, backup_dir: str) -> bool:
        """
        從備份還原規則檔案

        Args:
            backup_dir (str): 備份目錄

        Returns:
            bool: 還原是否成功
        """
        if not os.path.exists(backup_dir):
            self.logger.warning(f"備份目錄不存在: {backup_dir}")
            return False

        try:
            # 備份當前規則
            current_backup, _ = self.backup_rules()

            # 還原基本規則
            base_backup = os.path.join(backup_dir, os.path.basename(self.base_rules_path))
            if os.path.exists(base_backup):
                shutil.copy2(base_backup, self.base_rules_path)

            # 還原磁場規則
            field_backup = os.path.join(backup_dir, os.path.basename(self.field_rules_path))
            if os.path.exists(field_backup):
                shutil.copy2(field_backup, self.field_rules_path)

            # 還原其他規則檔案
            for filename in os.listdir(backup_dir):
                if filename.endswith(".json") and filename not in [os.path.basename(self.base_rules_path), os.path.basename(self.field_rules_path)]:
                    src = os.path.join(backup_dir, filename)
                    dst = os.path.join(self.rules_dir, filename)
                    shutil.copy2(src, dst)

            # 清除快取
            self.rules_cache.clear()
            self.last_update_time.clear()

            self.logger.info(f"成功從 {backup_dir} 還原規則檔案")
            return True
        except Exception as e:
            self.logger.error(f"還原規則檔案失敗: {e}")
            return False

# 測試用程式
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 創建規則庫
    repo = RuleRepository()

    # 驗證規則
    is_valid, errors = repo.validate_rules()
    print(f"規則是否有效: {is_valid}")
    if not is_valid:
        print("錯誤:")
        for error in errors:
            print(f"  - {error}")

    # 載入規則
    base_rules = repo.load_base_rules()
    field_rules = repo.load_field_rules()

    print("\n基本規則版本:", repo.get_base_rule_version())
    print("磁場規則版本:", repo.get_field_rule_version())

    # 顯示磁場對應
    magnetic_pairs = repo.get_magnetic_pairs()
    print("\n磁場對應:")
    for field, pairs in magnetic_pairs.items():
        print(f"  {field}: {', '.join(pairs)}")

    # 顯示磁場屬性
    magnetic_fields = repo.get_magnetic_fields()
    print("\n磁場屬性:")
    for field, attributes in magnetic_fields.items():
        print(f"  {field}:")
        for key, value in attributes.items():
            if isinstance(value, list):
                value = ', '.join(value)
            print(f"    {key}: {value}")

    # 查找特定數字對的磁場
    test_pair = "13"
    print(f"\n數字對 {test_pair} 對應的磁場: {repo.get_field_by_pair(test_pair)}")

    # 獲取特定磁場的屬性
    test_field = "天醫"
    field_attrs = repo.get_field_attributes(test_field)
    print(f"\n磁場 {test_field} 的屬性:")
    for key, value in field_attrs.items():
        print(f"  {key}: {value}")