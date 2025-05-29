from .input_data import InputType
from dataclasses import dataclass


@dataclass
class ResultData:
    input_type: InputType
    input_value: str
    raw_analysis: str | None
    counts: dict
    adjusted_counts: dict
    adjusted_log: list[str]
    recommendations: list
    field_details: dict
    errors: list[str]

    @classmethod
    def from_dict(cls, result_dict: dict):
        input_type = InputType(result_dict.get("input_type"))
        input_value = result_dict.get("input_value", "")
        raw_analysis = result_dict.get("raw_analysis")
        counts = result_dict.get("counts", {})
        adjusted_counts = result_dict.get("adjusted_counts", {})
        adjusted_log = result_dict.get("adjusted_log", [])
        recommendations = result_dict.get("recommendations", [])
        field_details = result_dict.get("field_details", {})
        errors = result_dict.get("errors", [])
        return ResultData(input_type=input_type,
                          input_value=input_value,
                          raw_analysis=raw_analysis,
                          counts=counts,
                          adjusted_counts=adjusted_counts,
                          adjusted_log=adjusted_log,
                          recommendations=recommendations,
                          field_details=field_details,
                          errors=errors)

    def to_dict(self):
        return {
            "input_type": self.input_type.value,
            "input_value": self.input_value,
            "raw_analysis": self.raw_analysis,
            "counts": self.counts,
            "adjusted_counts": self.adjusted_counts,
            "adjusted_log": self.adjusted_log,
            "recommendations": self.recommendations,
            "field_details": self.field_details,
            "errors": self.errors
        }
