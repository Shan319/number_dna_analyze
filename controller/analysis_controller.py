#  controller/analysis_controller.py
"""
數字DNA分析控制器
負責協調數據和處理流程
接收來自input_controller的用戶輸入
調用核心分析模組進行處理
將結果傳遞給result_controller顯示
"""

import logging
from collections import Counter

# 從核心模組導入分析功能
from core.field_analyzer import analyze_input, analyze_name_strokes, analyze_mixed_input
from core.number_analyzer import keyword_fields, magnetic_fields, analyze_magnetic_fields
from core.recommendation_engine import generate_multiple_lucky_numbers

logger = logging.getLogger("數字DNA分析器.AnalysisController")


def analyze(input_data):
    """
    分析用戶輸入數據
    Args:
        input_data (dict): 從input_controller收集的用戶輸入
    Returns:
        dict: 包含分析結果和推薦數字的字典
    """
    logger.info("開始分析用戶輸入數據")

    # 初始化結果字典
    result = {
        "input_type": "",
        "raw_analysis": "",
        "counts": {},
        "adjusted_counts": {},
        "recommendations": [],
        "field_details": {},
        "messages": []
    }

    try:
        # 決定輸入類型和分析方法
        if "name" in input_data and input_data["name"]:
            result["input_type"] = "姓名"
            raw_result = analyze_name_strokes(input_data["name"])
        elif "id" in input_data and input_data["id"]:
            result["input_type"] = "身分證"
            raw_result = analyze_input(input_data["id"], is_id=True)
        elif "birth" in input_data and input_data["birth"]:
            result["input_type"] = "生日"
            raw_result = analyze_input((input_data["birth"]).replace("/", ""))    
        elif "custom" in input_data and input_data["custom"]:
            # 處理自定義輸入 - 根據混合模式決定分析方法
            result["input_type"] = "自定義"
            if input_data.get("mix_mode", False):
                raw_result = analyze_mixed_input(input_data["custom"])
            else:
                raw_result = analyze_mixed_input(input_data["custom"])
        else:
            result["messages"].append("未提供有效的輸入數據")
            return result

        # 處理原始分析結果
        result["raw_analysis"] = raw_result
        magnetic_fields_list = raw_result.split()

        # # 計算磁場頻率
        # base_counts = Counter(magnetic_fields_list)
        # result["counts"] = dict(base_counts)

        # # 進階分析 - 套用規則調整磁場計數
        # adjusted_counts, adjust_log = apply_advanced_rules(magnetic_fields_list)
        # result["adjusted_counts"] = adjusted_counts
        # result["adjust_log"] = adjust_log

        # 使用 analyze_magnetic_fields 進行磁場分析
        base_counts, adjusted_counts, adjust_log = analyze_magnetic_fields(magnetic_fields_list)

        # 保存分析結果
        result["counts"] = dict(base_counts)
        result["adjusted_counts"] = adjusted_counts
        result["adjust_log"] = adjust_log

        # 生成推薦數字
        digit_length = int(input_data.get("digit_length", 4))
        if input_data.get("digit_length") == "custom":
            try:
                digit_length = int(input_data.get("custom_digit", 4))
            except ValueError:
                digit_length = 4
                result["messages"].append("自定義位數格式錯誤，使用預設值4")

        # 生成推薦數字
        result["recommendations"] = generate_lucky_numbers(adjusted_counts, digit_length)

        # 添加磁場詳細資訊
        result["field_details"] = generate_field_details(adjusted_counts)

        logger.info(f"分析完成: {result['input_type']}")
        return result

    except Exception as e:
        logger.error(f"分析過程發生錯誤: {e}", exc_info=True)
        result["messages"].append(f"分析錯誤: {str(e)}")
        return result


def apply_advanced_rules(input_list):
    """
    應用進階分析規則處理磁場序列
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


def generate_field_details(adjusted_counts):
    """
    生成各個磁場的詳細資訊
    Args:
        adjusted_counts (dict): 調整後的磁場計數
    Returns:
        dict: 包含磁場詳細資訊的字典
    """
    field_details = {}

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


def generate_lucky_numbers(adjusted_counts, length=4, count=5):
    """
    根據分析結果生成幸運數字
    Args:
        adjusted_counts (dict): 調整後的磁場計數
        length (int): 生成數字長度
        count (int): 生成數量
    Returns:
        list: 幸運數字列表
    """
    try:
        # 將adjust_counts轉換為generate_multiple_lucky_numbers函數所需的格式
        magnetic_input = {k: v for k, v in adjusted_counts.items()}

        # 使用核心推薦引擎生成數字
        lucky_numbers = generate_multiple_lucky_numbers(magnetic_input, length, count)
        return lucky_numbers
    except Exception as e:
        logger.error(f"生成幸運數字時發生錯誤: {e}", exc_info=True)
        return []
