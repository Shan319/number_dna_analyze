#  core/number_analyzer.py
from collections import Counter

# 磁場定義

keyword_fields = {
    "伏位": {"蓄勢待發、狀況延續、臥虎藏龍"},
    "生氣": {"貴人、轉機、好名聲"},
    "天醫": {"主大才、天生聰穎、文筆好"},
    "延年": {"意志堅定的領袖格局"},
    "絕命": {"高IQ低EQ、大起大落的極端特質"},
    "禍害": {"口舌、病弱、心機"},
    "五鬼": {"最有才華但最不穩定、際遇波折"},
    "六煞": {"情感、婚姻、或人際關係方面糾葛"},
}
magnetic_fields = {
    "伏位": {"strengths": "有耐心、責任心強、幽默風趣、善於溝通協調",
             "weaknesses": "矛盾交錯、沒有安全感、主觀意識強、作風保守",
             "financial_strategy": "耐心積累，穩健投資，適合選擇風險較低、回報穩定的金融產品",
             "relationship_advice": "尋求穩定與安全感，在互動中需要耐心溝通"},
    "生氣": {"strengths": "樂天派、凡事不強求、熱心助人、擁有好人緣",
             "weaknesses": "企圖心不旺盛，由於對任何事不強求隨遇而安",
             "financial_strategy": "積極開拓，慎選機遇，避免盲目跟風",
             "relationship_advice": "積極互動，珍惜緣分，避免過度追求新鮮感"},
    "天醫": {"strengths": "賺錢有如神助、諸事順遂、外型氣質俱佳",
             "weaknesses": "極度善良，偶爾會被蒙騙",
             "financial_strategy": "智慧投資，行善積福，防範詐騙",
             "relationship_advice": "關懷對方，共同成長，給予情感支持"},
    "延年": {"strengths": "決斷力強、內斂成熟",
             "weaknesses": "缺少彈性變通，做事強勢，一板一眼",
             "financial_strategy": "領導風範，規劃未來，長期財務規劃",
             "relationship_advice": "領導與支持，平衡關係，聆聽對方意見"},
    "絕命": {"strengths": "反應靈敏、善於謀略，重視精神層面",
             "weaknesses": "缺乏圓融、執著己見",
             "financial_strategy": "冷靜應對，規避風險，避免情緒化決策",
             "relationship_advice": "情緒管理，避免極端，冷靜處理糾紛"},
    "禍害": {"strengths": "辯才無礙、能言善道",
             "weaknesses": "口舌之爭不斷、身體狀況不佳",
             "financial_strategy": "口才服人，謹慎決策，避免過度自信",
             "relationship_advice": "慎選言辭，避免衝突，注意言辭影響"},
    "五鬼": {"strengths": "鬼才洋溢、快速的學習力",
             "weaknesses": "變動太快，難以產生安定力量",
             "financial_strategy": "創新思維，謹慎投資，避免忽視風險",
             "relationship_advice": "創新互動，忠誠為本，保持透明度"},
    "六煞": {"strengths": "異性緣特別好、具有俊男美女的外貌",
             "weaknesses": "總是為情所困，感情、事業、工作不順遂",
             "financial_strategy": "和諧人際，謹慎合作，明確權責界限",
             "relationship_advice": "和諧相處，避免糾纏，設定清晰界限"}
}

def analyze_magnetic_fields(input_list):
    """
    分析磁場並返回結果

    Args:
        input_list (list): 磁場名稱列表

    Returns:
        tuple: (base_counts, adjusted_counts, adjust_log)
        - base_counts: 原始磁場計數
        - adjusted_counts: 調整後的磁場計數
        - adjust_log: 調整日誌
    """
    # 初步計數
    base_counts = Counter(input_list)

    # 進階規則處理
    adjusted_counts = base_counts.copy()
    adjust_log = []

    # 使用 try-except 以防磁場名稱不在預定義列表中
    try:
        # 規則 1：天醫 vs 絕命 抵銷
        cancel_count = min(adjusted_counts.get("天醫", 0), adjusted_counts.get("絕命", 0))
        if cancel_count > 0:
            adjusted_counts["天醫"] -= cancel_count
            adjusted_counts["絕命"] -= cancel_count
            adjust_log.append(f"(天醫-{cancel_count})")
            adjust_log.append(f"(絕命-{cancel_count})")

        # 規則 2：延年 vs 六煞 抵銷
        cancel_count = min(adjusted_counts.get("延年", 0), adjusted_counts.get("六煞", 0))
        if cancel_count > 0:
            adjusted_counts["延年"] -= cancel_count
            adjusted_counts["六煞"] -= cancel_count
            adjust_log.append(f"(延年-{cancel_count})")
            adjust_log.append(f"(六煞-{cancel_count})")

        # 規則 3：固定對組合 -> 抵一個禍害
        group_pairs = [("生氣", "生氣"), ("生氣", "延年"), ("生氣", "伏位"), ("延年", "生氣")]
        i = 0
        used_indexes = set()
        while i < len(input_list) - 1:
            pair = (input_list[i], input_list[i+1])
            if pair in group_pairs and adjusted_counts.get("禍害", 0) > 0:
                adjust_log.append(f"({pair[0]}-1) ({pair[1]}-1) (禍害-1)")
                adjusted_counts[pair[0]] -= 1
                adjusted_counts[pair[1]] -= 1
                adjusted_counts["禍害"] -= 1
                used_indexes.update([i, i+1])
                i += 2
            else:
                i += 1

        # 規則 4：生氣+天醫+延年 -> 抵五鬼
        i = 0
        while i < len(input_list) - 2:
            triplet = input_list[i:i+3]
            if triplet == ["生氣", "天醫", "延年"] and adjusted_counts.get("五鬼", 0) > 0:
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

            if count > 0 and adjusted_counts.get("伏位", 0) >= count:
                adjusted_counts[input_list[i]] += count
                adjusted_counts["伏位"] -= count
                adjust_log.append(f"({input_list[i]}+{count}) (伏位-{count})")
                for k in range(i, j):
                    used_indexes.add(k)
                i = j
            else:
                i += 1
    except Exception as e:
        # 處理可能的錯誤，例如磁場名稱不在預定義列表中
        print(f"分析磁場時發生錯誤: {e}")

    # 移除計數為0的項目
    adjusted_counts = {k: v for k, v in adjusted_counts.items() if v > 0}

    return base_counts, adjusted_counts, adjust_log

