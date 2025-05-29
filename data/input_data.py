from enum import Enum, auto
from dataclasses import dataclass


class InputType(Enum):
    NONE = "未知類型"
    NAME = "姓名"
    ID = "身分證"
    PHONE = "手機號碼"
    BIRTH = "生日"
    CUSTOM = "自定義"


class FixDigitsPosition(Enum):
    NONE = auto()
    BEGIN = "前"
    CENTER = "中"
    END = "後"


@dataclass
class InputData:
    input_type: InputType
    input_value: str
    custom_digits_length: bool
    digits_length: int | str
    fixed_digits_position: FixDigitsPosition
    fixed_digits_value: str
    default_conditions: dict[str, bool]
    other_conditions: dict[str, bool]
