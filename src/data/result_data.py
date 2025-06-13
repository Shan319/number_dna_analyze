from datetime import datetime

from pydantic import BaseModel

from .input_data import InputData


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


class HistoryData(BaseModel):
    path: str
    date: datetime
    raw: ResultData
