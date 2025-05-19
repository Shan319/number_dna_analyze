import random

# 每種磁場對應的兩位數字組合
magneticic_pairs = {
    "伏位": ["11", "22", "33", "44", "66", "77", "88", "99"],
    "生氣": ["14", "41", "67", "76", "39", "93", "28", "82"],
    "天醫": ["13", "31", "68", "86", "49", "94", "27", "72"],
    "延年": ["19", "91", "78", "87", "34", "43", "26", "62"]
}

# 產生抵銷表 & 五鬼三連段數量
def generate_lucky_numbers(magnetic_fields):
    fields = magnetic_fields.copy()
    cancel_fields = {"天醫": 0, "生氣": 0, "伏位": 0, "延年": 0}

    wugui_count = fields.get("五鬼", 0)
    cancel_fields["天醫"] += wugui_count
    cancel_fields["生氣"] += wugui_count
    cancel_fields["延年"] += wugui_count

    cancel_fields["天醫"] += fields.get("絕命", 0)
    cancel_fields["延年"] += fields.get("六煞", 0)

    for _ in range(fields.get("禍害", 0)):
        cancel_fields["生氣"] += 1
        r = random.choice(["生氣", "伏位", "延年"])
        cancel_fields[r] += 1

    return cancel_fields, wugui_count

# 尋找一組生氣→天醫→延年 三連段（尾接頭）
def find_triplet():
    triplets = []
    for p1 in magneticic_pairs["生氣"]:
        for p2 in magneticic_pairs["天醫"]:
            if p1[1] != p2[0]:
                continue
            for p3 in magneticic_pairs["延年"]:
                if p2[1] == p3[0]:
                    triplets.append([("生氣", p1), ("天醫", p2), ("延年", p3)])
    return random.choice(triplets) if triplets else []

# 根據 cancel_fields 與 wugui 數量 建立幸運數字
def generate_lucky_number_chain_by_cancel_fields(cancel_fields, length, num_triplets):
    num_fields = length - 1
    magnetic_sequence = []
    remaining_fields = cancel_fields.copy()

    # 優先塞入 num_triplets 組 三連段（抵銷五鬼）
    for _ in range(num_triplets):
        if (remaining_fields.get("生氣", 0) >= 1 and
            remaining_fields.get("天醫", 0) >= 1 and
            remaining_fields.get("延年", 0) >= 1):
            triplet = find_triplet()
            if triplet:
                for field, pair in triplet:
                    magnetic_sequence.append(pair)
                    remaining_fields[field] -= 1

    # 接續其他磁場對
    while len(magnetic_sequence) < num_fields:
        last_digit = magnetic_sequence[-1][1] if magnetic_sequence else None
        candidates = []

        for field in ["天醫", "生氣", "伏位", "延年"]:
            if remaining_fields.get(field, 0) > 0:
                for pair in magneticic_pairs[field]:
                    if last_digit is None or pair[0] == last_digit:
                        candidates.append((field, pair))

        if candidates:
            field, pair = random.choice(candidates)
            magnetic_sequence.append(pair)
            remaining_fields[field] -= 1
        else:
            if last_digit:
                for pair in magneticic_pairs["伏位"]:
                    if pair[0] == last_digit:
                        magnetic_sequence.append(pair)
                        break
            break

    # 組合成幸運數字字串
    if not magnetic_sequence:
        return ""
    result = magnetic_sequence[0]
    for i in range(1, len(magnetic_sequence)):
        result += magnetic_sequence[i][1]

    return result

# 產生多組幸運數字
def generate_multiple_lucky_numbers(magnetic_input, length, count=15):
    cancel, wugui_triplets = generate_lucky_numbers(magnetic_input)
    results = []
    for _ in range(count):
        lucky = generate_lucky_number_chain_by_cancel_fields(cancel, length, wugui_triplets)
        results.append(lucky)
    return results
