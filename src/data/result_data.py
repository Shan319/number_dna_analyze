from datetime import datetime
from typing import Self

from pydantic import BaseModel

from .input_data import InputData
from src.utils import main_service


class FieldDetail(BaseModel):
    count: int
    keywords: list[str]
    strengths: str
    weaknesses: str
    financial_strategy: str
    relationship_advice: str


class ResultData(BaseModel):
    input_data: InputData
    raw_analysis: str | None
    counts: dict[str, int]
    adjusted_counts: dict[str, int]
    adjusted_log: list[str]
    recommendations: list[str]
    field_details: dict[str, FieldDetail]
    errors: list[str]

    def write_history(self, date: datetime | None = None):
        if date is None:
            date = datetime.now()
        full_path = main_service.file_manager.get_history_path(date)
        raw = self.model_dump()
        main_service.file_manager.write_to_json(full_path, raw)


class HistoryData(BaseModel):
    path: str
    date: datetime
    raw: ResultData

    @classmethod
    def read_all_histories(cls) -> list[Self]:
        histories: list[Self] = []

        history_paths = main_service.file_manager.list_all_history_paths()
        for full_path, date in history_paths:
            raw = main_service.file_manager.read_from_json(full_path)
            history_data = cls(path=full_path, date=date, raw=raw)
            histories.append(history_data)

        return histories
