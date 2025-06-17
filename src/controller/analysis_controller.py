#  controller/analysis_controller.py
"""
數字 DNA 分析控制器
負責協調數據和處理流程
接收來自input_controller的用戶輸入
調用核心分析模組進行處理
將結果傳遞給result_controller顯示
"""

from collections import Counter
from typing import Any

# 從核心模組導入分析功能
from src.utils import main_service
from src.data.input_data import InputData, InputType, FixDigitsPosition
from src.data.result_data import ResultData, FieldDetail
from src.core.field_analyzer import analyze_input, analyze_name_strokes, analyze_mixed_input
from src.core.number_analyzer import keyword_fields, magnetic_fields, analyze_magnetic_fields
from src.core.recommendation_engine import generate_multiple_lucky_numbers


def get_logger():
    return main_service.log.get_logger("數字 DNA 分析器.AnalysisController")


def analyze(input_data: InputData) -> ResultData:
    """分析用戶輸入數據

    Parameters
    ----------
    input_data : InputData
        輸入數據

    Returns
    -------
    ResultData
        分析結果
    """
    logger = get_logger()
    logger.info("開始分析用戶輸入數據")

    errors: list[str] = []

    input_type = input_data.input_type
    input_value = input_data.input_value
    result_data = ResultData(input_data=input_data,
                             raw_analysis=None,
                             counts={},
                             adjusted_counts={},
                             adjusted_log=[],
                             recommendations=[],
                             field_details={},
                             errors=[])
    try:
        raw_analysis = None

        if input_type == InputType.NAME:
            raw_analysis = analyze_name_strokes(input_value)
        elif input_type == InputType.ID:
            raw_analysis = analyze_input(input_value, is_id=True)
        elif input_type == InputType.BIRTH:
            raw_analysis = analyze_input(input_value.replace("/", ""))
        elif input_type == InputType.PHONE:
            raw_analysis = analyze_input(input_value)
        elif input_type == InputType.CUSTOM:
            raw_analysis = analyze_mixed_input(input_value)

        result_data.raw_analysis = raw_analysis

        # 處理原始分析結果
        if not raw_analysis:  # 檢查空結果
            errors.append("分析結果為空，請檢查輸入數據")
            return result_data

        magnetic_fields_list = raw_analysis.split()
        # 使用 analyze_magnetic_fields 進行磁場分析
        base_counts, adjusted_counts, adjust_log = analyze_magnetic_fields(magnetic_fields_list)
        result_data.counts = base_counts
        result_data.adjusted_counts = adjusted_counts
        result_data.adjusted_log = adjust_log

        # 生成推薦數字
        result_data.recommendations = generate_full_lucky_numbers(adjusted_counts, input_data)

        # 添加磁場詳細資訊
        field_details = generate_field_details(adjusted_counts)
        for field_name, field_detail in field_details.items():
            result_data.field_details[field_name] = FieldDetail(**field_detail)

        logger.info(f"分析完成: {result_data.input_data.input_type}")
        return result_data

    except Exception as e:
        logger.error(f"分析過程發生錯誤: {e}", exc_info=True)
        errors.append(f"分析錯誤: {str(e)}")
        return result_data


def apply_advanced_rules(input_list):
    """
    [TODO] 應用進階分析規則處理磁場序列
    Args:
        input_list (list): 磁場名稱列表
    Returns:
        tuple: (調整後的計數字典, 調整日誌)
    """
    # 初步計數
    base_counts = Counter(input_list)
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
    group_pairs = [("天醫", "天醫"), ("天醫", "延年"), ("生氣", "伏位"), ("延年", "生氣")]
    i = 0
    while i < len(input_list) - 1:
        pair = (input_list[i], input_list[i + 1])
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
    while i < len(input_list) - 2:
        triplet = input_list[i:i + 3]
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
    while i < len(input_list) - 1:
        if i in used_indexes or input_list[i] == "伏位":
            i += 1
            continue

        count = 0
        j = i + 1
        while j < len(input_list) and input_list[j] == "伏位" and j not in used_indexes:
            count += 1
            j += 1

        if count > 0 and adjusted_counts["伏位"] >= count:
            adjusted_counts[input_list[i]] += count
            adjusted_counts["伏位"] -= count
            adjust_log.append(f"({input_list[i]}+{count}) (伏位-{count})")
            for k in range(i, j):
                used_indexes.add(k)
            i = j
        else:
            i += 1

    # 移除計數為0的項目
    adjusted_counts = {k: v for k, v in adjusted_counts.items() if v > 0}

    return adjusted_counts, adjust_log


def generate_field_details(adjusted_counts: dict[str, int]) -> dict[str, Any]:
    """生成各個磁場的詳細資訊

    Parameters
    ----------
    adjusted_counts : dict[str, int]
        調整後的磁場計數

    Returns
    -------
    dict[str, Any]
        包含磁場詳細資訊的字典
    """
    field_details: dict[str, Any] = {}

    for field, count in adjusted_counts.items():
        if count <= 0:
            continue

        field_details[field] = {
            "count": count,
            "keywords": keyword_fields.get(field, {"未知關鍵字"}),
            "strengths": magnetic_fields.get(field, {}).get("strengths", "無資料"),
            "weaknesses": magnetic_fields.get(field, {}).get("weaknesses", "無資料"),
            "financial_strategy": magnetic_fields.get(field, {}).get("financial_strategy", "無資料"),
            "relationship_advice": magnetic_fields.get(field, {}).get("relationship_advice", "無資料")
        }

    return field_details


def generate_lucky_numbers(adjusted_counts: dict[str, int], length=4, count=5) -> list[str]:
    """根據分析結果生成幸運數字

    Parameters
    ----------
    adjusted_counts : dict[str, int]
        調整後的磁場計數
    length : int, optional
        生成數字長度, by default 4
    count : int, optional
        生成數量, by default 5

    Returns
    -------
    list[str]
        幸運數字列表
    """
    logger = get_logger()

    try:
        # 將adjust_counts轉換為generate_multiple_lucky_numbers函數所需的格式
        magnetic_input = {k: v for k, v in adjusted_counts.items()}

        # 使用核心推薦引擎生成數字
        lucky_numbers = generate_multiple_lucky_numbers(magnetic_input, length, count)
        return lucky_numbers
    except Exception as e:
        logger.error(f"生成幸運數字時發生錯誤: {e}", exc_info=True)
        return []


def generate_full_lucky_numbers(adjusted_counts: dict[str, int],
                                input_data: InputData,
                                count: int = 5) -> list[str]:
    digits_length = int(input_data.digits_length)
    fixed_digits_position = input_data.fixed_digits_position
    fixed_digits_value = input_data.fixed_digits_value
    if fixed_digits_position != FixDigitsPosition.NONE:
        digits_length = digits_length - len(fixed_digits_value)

    # 生成推薦數字
    recommendations = generate_lucky_numbers(adjusted_counts, digits_length, count)

    # 插入固定英數字
    if fixed_digits_position != FixDigitsPosition.NONE:
        new_recommendations: list[str] = []
        for recommendation in recommendations:
            prev = ""
            post = ""
            if fixed_digits_position == FixDigitsPosition.BEGIN:
                post = recommendation
            elif fixed_digits_position == FixDigitsPosition.CENTER:
                prev = recommendation[:(digits_length + 1) // 2]
                post = recommendation[(digits_length + 1) // 2:]
            elif fixed_digits_position == FixDigitsPosition.END:
                prev = recommendation
            new_recommendation = prev + fixed_digits_value + post
            new_recommendations.append(new_recommendation)

        recommendations = new_recommendations

    return recommendations
