import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, field_serializer

from src.utils import main_service


class InputType(str, Enum):
    NONE = "未知類型"
    NAME = "姓名"
    ID = "身分證"
    PHONE = "手機號碼"
    BIRTH = "生日"
    CUSTOM = "自定義"


class FixDigitsPosition(str, Enum):
    NONE = "不添加"
    BEGIN = "前"
    CENTER = "中"
    END = "後"


_default_input_value = {
    name: ""
    for name in [
        InputType.NAME.value,
        InputType.ID.value,
        InputType.PHONE.value,
        InputType.BIRTH.value,
        InputType.CUSTOM.value,
    ]
}
_default_default_conditions = {name: True for name in ["絕命", "五鬼", "六煞", "禍害"]}
_default_other_conditions = {name: False for name in ["延年", "天醫", "生氣", "伏位"]}


class InputData(BaseModel):
    input_type: InputType = InputType.NAME
    input_values: dict[str, str] = Field(default_factory=lambda: _default_input_value)
    is_custom_digits_length: bool = False
    digits_length: int | str = "4"
    fixed_digits_position: FixDigitsPosition = FixDigitsPosition.NONE
    fixed_digits_value: str = ""
    default_conditions: dict[str, bool] = Field(default_factory=lambda: _default_default_conditions)
    other_conditions: dict[str, bool] = Field(default_factory=lambda: _default_other_conditions)

    @classmethod
    def get_defaults(cls):
        return InputData()

    @property
    def input_value(self):
        return self.input_values[self.input_type.value]

    @field_serializer("input_values")
    def encrypt_input_values(self, value: dict[str, str], _info):
        plain = json.dumps(value)
        return main_service.cryptography.encrypt(plain)

    @field_validator("input_values", mode="before")
    @classmethod
    def decrypt_input_values(cls, value: Any):
        if not isinstance(value, str):
            raise ValueError(f"value should be str")
        plain = main_service.cryptography.decrypt(value)
        return json.loads(plain)

    def write_settings(self):
        full_path = main_service.file_manager.get_settings_path()
        raw = self.model_dump()
        main_service.file_manager.dump_to_json_file(full_path, raw)

    @classmethod
    def read_settings(cls):
        full_path = main_service.file_manager.get_settings_path()
        raw = main_service.file_manager.load_from_json_file(full_path)
        input_data = InputData(**raw)
        return input_data
