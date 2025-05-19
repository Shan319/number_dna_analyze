# data/models.py
"""
數字DNA分析器 - 資料模型
定義應用程式中使用的核心資料結構和模型

功能：
1. 提供應用程式核心資料結構的定義
2. 實作資料驗證與轉換功能
3. 支援資料序列化與反序列化
4. 定義模組間資料交換的標準格式
5. 提供模型轉換和匯出功能
"""

import json
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field, asdict

# 定義常數
MAGNETIC_FIELD_TYPES = {
    "伏位", "延年", "生氣", "天醫", "六煞", "絕命", "禍害", "五鬼"
}

FIELD_ATTRIBUTES = [
    "keywords", "strengths", "weaknesses",
    "financial_strategy", "relationship_advice"
]

@dataclass
class MagneticField:
    """磁場模型，定義磁場的屬性和特性"""

    name: str  # 磁場名稱
    count: int = 0  # 出現次數
    keywords: List[str] = field(default_factory=list)  # 關鍵字
    strengths: str = ""  # 優勢
    weaknesses: str = ""  # 弱點
    financial_strategy: str = ""  # 財務建議
    relationship_advice: str = ""  # 關係建議

    def __post_init__(self):
        """初始化後驗證"""
        if self.name not in MAGNETIC_FIELD_TYPES:
            raise ValueError(f"無效的磁場名稱: {self.name}")

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "name": self.name,
            "count": self.count,
            "keywords": self.keywords,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "financial_strategy": self.financial_strategy,
            "relationship_advice": self.relationship_advice
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MagneticField':
        """從字典建立實例"""
        # 確保關鍵字是列表
        if "keywords" in data and isinstance(data["keywords"], str):
            data["keywords"] = [k.strip() for k in data["keywords"].split("、")]

        return cls(**data)

@dataclass
class InputData:
    """輸入資料模型，儲存使用者輸入的原始資料"""

    input_type: str  # 輸入類型: "name", "id", "custom"
    value: str  # 輸入值
    options: Dict[str, Any] = field(default_factory=dict)  # 分析選項
    timestamp: float = field(default_factory=datetime.datetime.now().timestamp)  # 時間戳

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "input_type": self.input_type,
            "value": self.value,
            "options": self.options,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputData':
        """從字典建立實例"""
        return cls(**data)

    def validate(self) -> Tuple[bool, List[str]]:
        """驗證輸入是否有效"""
        errors = []

        # 檢查輸入類型
        if self.input_type not in ["name", "id", "custom"]:
            errors.append(f"無效的輸入類型: {self.input_type}")

        # 檢查輸入值
        if not self.value:
            errors.append("輸入值不能為空")

        # 根據輸入類型進行特定驗證
        if self.input_type == "id" and len(self.value) == 10:
            if not (self.value[0].isalpha() and self.value[1:].isdigit()):
                errors.append("身分證格式不正確")

        return len(errors) == 0, errors

@dataclass
class AnalysisResult:
    """分析結果模型，儲存分析引擎產生的結果"""

    input_data: InputData  # 輸入資料
    raw_analysis: str  # 原始分析字串
    counts: Dict[str, int]  # 磁場計數
    adjusted_counts: Dict[str, int]  # 調整後磁場計數
    adjust_log: List[str] = field(default_factory=list)  # 調整日誌
    recommendations: List[str] = field(default_factory=list)  # 推薦數字
    field_details: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # 磁場詳細資訊
    messages: List[str] = field(default_factory=list)  # 訊息/警告
    timestamp: float = field(default_factory=datetime.datetime.now().timestamp)  # 時間戳

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "input_type": self.input_data.input_type,
            "input_value": self.input_data.value,
            "input_options": self.input_data.options,
            "raw_analysis": self.raw_analysis,
            "counts": self.counts,
            "adjusted_counts": self.adjusted_counts,
            "adjust_log": self.adjust_log,
            "recommendations": self.recommendations,
            "field_details": self.field_details,
            "messages": self.messages,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """從字典建立實例"""
        # 創建輸入資料對象
        input_data = InputData(
            input_type=data.get("input_type", ""),
            value=data.get("input_value", ""),
            options=data.get("input_options", {}),
            timestamp=data.get("timestamp", datetime.datetime.now().timestamp())
        )

        # 創建分析結果對象
        return cls(
            input_data=input_data,
            raw_analysis=data.get("raw_analysis", ""),
            counts=data.get("counts", {}),
            adjusted_counts=data.get("adjusted_counts", {}),
            adjust_log=data.get("adjust_log", []),
            recommendations=data.get("recommendations", []),
            field_details=data.get("field_details", {}),
            messages=data.get("messages", []),
            timestamp=data.get("timestamp", datetime.datetime.now().timestamp())
        )

    def summary(self) -> Dict[str, Any]:
        """生成結果摘要"""
        # 計算總磁場數
        total_fields = sum(self.adjusted_counts.values())

        # 計算正向和負向磁場數
        positive_fields = sum(self.adjusted_counts.get(field, 0)
                             for field in ["天醫", "生氣", "延年", "伏位"])
        negative_fields = sum(self.adjusted_counts.get(field, 0)
                             for field in ["五鬼", "六煞", "禍害", "絕命"])

        # 計算比例
        positive_ratio = positive_fields / total_fields if total_fields > 0 else 0
        negative_ratio = negative_fields / total_fields if total_fields > 0 else 0

        return {
            "total_fields": total_fields,
            "positive_fields": positive_fields,
            "negative_fields": negative_fields,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "dominant_fields": self._get_dominant_fields(),
            "recommendation_count": len(self.recommendations)
        }

    def _get_dominant_fields(self, top_n: int = 3) -> List[str]:
        """獲取主要的磁場（出現次數最多的前N個）"""
        # 按出現次數排序
        sorted_fields = sorted(
            self.adjusted_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 返回前N個
        return [field for field, _ in sorted_fields[:top_n]]

    def export_to_json(self) -> str:
        """匯出為JSON字串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def export_to_text(self) -> str:
        """匯出為可讀文本格式"""
        # 格式化時間
        time_str = datetime.datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        # 構建輸出文本
        lines = [
            "數字DNA分析結果",
            "=" * 50,
            f"分析時間: {time_str}",
            f"輸入類型: {self.input_data.input_type}",
            f"輸入值: {self.input_data.value}",
            "",
            "原始磁場統計:",
        ]

        for field, count in self.counts.items():
            lines.append(f"  {field}: {count}")

        lines.append("")
        lines.append("調整規則:")
        for log in self.adjust_log:
            lines.append(f"  {log}")

        lines.append("")
        lines.append("調整後磁場統計:")
        for field, count in self.adjusted_counts.items():
            lines.append(f"  {field}: {count}")

        lines.append("")
        lines.append("推薦幸運數字:")
        for idx, num in enumerate(self.recommendations, 1):
            lines.append(f"  {idx}. {num}")

        lines.append("")
        lines.append("磁場詳細資訊:")
        for field, details in self.field_details.items():
            if field not in self.adjusted_counts:
                continue

            lines.append(f"  {field} (出現 {self.adjusted_counts[field]} 次):")

            # 關鍵字
            keywords = details.get("keywords", [])
            if isinstance(keywords, list):
                keyword_str = "、".join(keywords)
            else:
                keyword_str = keywords
            lines.append(f"    關鍵字: {keyword_str}")

            # 其他屬性
            for attr in ["strengths", "weaknesses", "financial_strategy", "relationship_advice"]:
                if attr in details and details[attr]:
                    attr_name = {
                        "strengths": "優勢",
                        "weaknesses": "弱點",
                        "financial_strategy": "財務建議",
                        "relationship_advice": "關係建議"
                    }.get(attr, attr)
                    lines.append(f"    {attr_name}: {details[attr]}")

            lines.append("")

        # 如果有訊息，添加到輸出
        if self.messages:
            lines.append("訊息:")
            for msg in self.messages:
                lines.append(f"  {msg}")

        return "\n".join(lines)

@dataclass
class MagneticPair:
    """磁場對應數字對模型，定義磁場與數字對的對應關係"""

    field: str  # 磁場名稱
    number_pairs: List[str]  # 數字對列表

    def __post_init__(self):
        """初始化後驗證"""
        if self.field not in MAGNETIC_FIELD_TYPES:
            raise ValueError(f"無效的磁場名稱: {self.field}")

        # 確保所有數字對有效
        for pair in self.number_pairs:
            if not (len(pair) == 2 and pair.isdigit()):
                raise ValueError(f"無效的數字對: {pair}")

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "field": self.field,
            "number_pairs": self.number_pairs
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MagneticPair':
        """從字典建立實例"""
        return cls(**data)

@dataclass
class RuleModel:
    """規則模型，定義磁場分析中使用的規則"""

    rule_id: str  # 規則ID
    description: str  # 規則描述
    type: str  # 規則類型
    priority: int = 0  # 優先級
    conditions: Dict[str, Any] = field(default_factory=dict)  # 條件
    actions: Dict[str, Any] = field(default_factory=dict)  # 動作

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "type": self.type,
            "priority": self.priority,
            "conditions": self.conditions,
            "actions": self.actions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleModel':
        """從字典建立實例"""
        return cls(**data)

    def matches(self, context: Dict[str, Any]) -> bool:
        """檢查規則是否匹配上下文"""
        # 根據規則類型執行不同的匹配邏輯
        if self.type == "cancel":
            # 抵消規則：檢查兩個磁場是否都存在
            field1 = self.conditions.get("field1")
            field2 = self.conditions.get("field2")

            if field1 and field2:
                return (
                    context.get("counts", {}).get(field1, 0) > 0 and
                    context.get("counts", {}).get(field2, 0) > 0
                )

        elif self.type == "sequence":
            # 序列規則：檢查特定序列是否存在
            sequence = self.conditions.get("sequence", [])
            fields = context.get("fields", [])

            if sequence and fields:
                # 檢查序列是否為fields的子序列
                return self._is_subsequence(sequence, fields)

        # 默認返回False
        return False

    def _is_subsequence(self, seq: List[str], fields: List[str]) -> bool:
        """檢查seq是否為fields的子序列"""
        seq_len = len(seq)
        fields_len = len(fields)

        if seq_len > fields_len:
            return False

        for i in range(fields_len - seq_len + 1):
            if fields[i:i+seq_len] == seq:
                return True

        return False

@dataclass
class UserProfile:
    """使用者個人資料模型"""

    name: str = ""  # 姓名
    id_number: str = ""  # 身分證號
    birth_date: str = ""  # 生日
    phone: str = ""  # 手機號碼
    email: str = ""  # 電子郵件
    custom_fields: Dict[str, str] = field(default_factory=dict)  # 自定義欄位
    preferences: Dict[str, Any] = field(default_factory=dict)  # 偏好設定

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典表示"""
        return {
            "name": self.name,
            "id_number": self.id_number,
            "birth_date": self.birth_date,
            "phone": self.phone,
            "email": self.email,
            "custom_fields": self.custom_fields,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """從字典建立實例"""
        return cls(**data)

    def validate(self) -> Tuple[bool, List[str]]:
        """驗證個人資料是否有效"""
        errors = []

        # 驗證身分證號
        if self.id_number and not self._validate_id_number(self.id_number):
            errors.append("身分證號格式不正確")

        # 驗證生日格式
        if self.birth_date and not self._validate_date_format(self.birth_date):
            errors.append("生日格式不正確 (應為 YYYY/MM/DD)")

        # 驗證手機號碼
        if self.phone and not self._validate_phone(self.phone):
            errors.append("手機號碼格式不正確")

        # 驗證電子郵件
        if self.email and not self._validate_email(self.email):
            errors.append("電子郵件格式不正確")

        return len(errors) == 0, errors

    def _validate_id_number(self, id_number: str) -> bool:
        """驗證身分證號"""
        import re
        return bool(re.match(r"^[A-Z][12]\d{8}$", id_number))

    def _validate_date_format(self, date_str: str) -> bool:
        """驗證日期格式"""
        import re
        return bool(re.match(r"^\d{4}/\d{2}/\d{2}$", date_str))

    def _validate_phone(self, phone: str) -> bool:
        """驗證手機號碼"""
        import re
        return bool(re.match(r"^09\d{8}$", phone))

    def _validate_email(self, email: str) -> bool:
        """驗證電子郵件"""
        import re
        return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))

# 工具函數

def convert_to_model(data: Dict[str, Any], model_class) -> Any:
    """轉換字典為模型實例"""
    return model_class.from_dict(data)

def convert_to_dict(model) -> Dict[str, Any]:
    """轉換模型實例為字典"""
    if hasattr(model, 'to_dict'):
        return model.to_dict()
    return asdict(model)

def validate_model(model) -> Tuple[bool, List[str]]:
    """驗證模型是否有效"""
    if hasattr(model, 'validate'):
        return model.validate()
    return True, []

# 測試用程式
if __name__ == "__main__":
    # 測試磁場模型
    field = MagneticField(
        name="天醫",
        count=2,
        keywords=["主大才", "天生聰穎", "文筆好"],
        strengths="賺錢有如神助、諸事順遂、外型氣質俱佳",
        weaknesses="極度善良，偶爾會被蒙騙",
        financial_strategy="智慧投資，行善積福，防範詐騙",
        relationship_advice="關懷對方，共同成長，給予情感支持"
    )
    print("磁場模型:", field)
    print("轉換為字典:", field.to_dict())
    print()

    # 測試輸入資料模型
    input_data = InputData(
        input_type="name",
        value="測試姓名",
        options={"digit_length": 4, "mix_mode": False}
    )
    print("輸入資料模型:", input_data)
    print("驗證結果:", input_data.validate())
    print()

    # 測試分析結果模型
    result = AnalysisResult(
        input_data=input_data,
        raw_analysis="天醫 生氣 延年 五鬼",
        counts={"天醫": 1, "生氣": 1, "延年": 1, "五鬼": 1},
        adjusted_counts={"天醫": 1, "生氣": 1, "延年": 1},
        adjust_log=["(五鬼-1)"],
        recommendations=["1234", "5678", "9012"],
        field_details={
            "天醫": {
                "count": 1,
                "keywords": ["主大才", "天生聰穎", "文筆好"],
                "strengths": "賺錢有如神助、諸事順遂、外型氣質俱佳",
                "weaknesses": "極度善良，偶爾會被蒙騙"
            }
        }
    )
    print("分析結果摘要:", result.summary())
    print("分析結果文本輸出:")
    print(result.export_to_text())
