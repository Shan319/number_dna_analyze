import random

# 生成增強磁場
def create_boost_field(tienyi, shenchi, yenien):
    boost_fields = dict()
    if tienyi:
        boost_fields["天醫"] = 1
    if shenchi:
        boost_fields["生氣"] = 1
    if yenien:
        boost_fields["延年"] = 1

    return boost_fields

boost_fields = create_boost_field(tienyi, shenchi, yenien)


# 每種磁場對應的兩位數字組合
magneticic_pairs = {
    "伏位": ["11", "22", "33", "44", "66", "77", "88", "99"],
    "生氣": ["14", "41", "67", "76", "39", "93", "28", "82"],
    "天醫": ["13", "31", "68", "86", "49", "94", "27", "72"],
    "延年": ["19", "91", "78", "87", "34", "43", "26", "62"]
}


# 產生抵銷表 & 五鬼三連段數量
def cancel_negative_magnetic_field(magnetic_fields):
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
def generate_lucky_number(cancel_fields, length, num_triplets, boost_fields):
    num_fields = length - 1
    magnetic_sequence = []
    remaining_fields = cancel_fields.copy()

    for _ in range(num_triplets):
        if (remaining_fields.get("生氣", 0) >= 1 and
            remaining_fields.get("天醫", 0) >= 1 and
            remaining_fields.get("延年", 0) >= 1):
            triplet = find_triplet()
            if triplet:
                for field, pair in triplet:
                    magnetic_sequence.append(pair)
                    remaining_fields[field] -= 1

    while len(magnetic_sequence) < num_fields:
        last_digit = magnetic_sequence[-1][1] if magnetic_sequence else None
        candidates = []

        for field in ["天醫", "生氣", "伏位", "延年"]:
            if remaining_fields.get(field, 0) > 0:
                for pair in magneticic_pairs[field]:
                    if last_digit is None or pair[0] == last_digit:
                        candidates.append((field, pair))

        if not candidates:
            break  # 跳出 while，轉交給 boost or fallback
        field, pair = random.choice(candidates)
        magnetic_sequence.append(pair)
        remaining_fields[field] -= 1

    if boost_fields:
        for field in boost_fields:
            if field in magneticic_pairs:
                last_digit = magnetic_sequence[-1][1] if magnetic_sequence else None
                valid_boosts = [p for p in magneticic_pairs[field] if last_digit is None or p[0] == last_digit]
                if valid_boosts:
                    magnetic_sequence.append(random.choice(valid_boosts))
                else:
                    magnetic_sequence.append(random.choice(magneticic_pairs[field]))


    while len(magnetic_sequence) < num_fields:
        last_digit = magnetic_sequence[-1][1] if magnetic_sequence else None
        # 嘗試找到可以接上的伏位 pair
        found = False
        for pair in magneticic_pairs["伏位"]:
            if last_digit is None or pair[0] == last_digit:
                magnetic_sequence.append(pair)
                found = True
                break
        # 如果找不到相連的伏位組合，也直接隨機補一組
        if not found:
            magnetic_sequence.append(random.choice(magneticic_pairs["伏位"]))


    if not magnetic_sequence:
        return ""
    result = magnetic_sequence[0]
    for i in range(1, len(magnetic_sequence)):
        result += magnetic_sequence[i][1]

    return result[:length]


def generate_final_lucky_number(magnetic_fields, total_length, fixed_part="", position="front"):
    # Step 1: 計算剩餘可用長度
    lucky_length = total_length - len(fixed_part)
    if lucky_length < 2:
        return fixed_part[:total_length]  # 無法產生有效幸運碼，只能裁切固定字串

    # Step 2: 取得正向磁場需求與三連段數
    cancel_fields, wugui_count = cancel_negative_magnetic_field(magnetic_fields)

    # Step 3: 產生幸運數字（需 lucky_length 長度）
    lucky_number = generate_lucky_number(cancel_fields, lucky_length, wugui_count)

    # Step 4: 插入固定字串
    if position == "front":
        result = fixed_part + lucky_number
    elif position == "middle":
        mid = len(lucky_number) // 2
        result = lucky_number[:mid] + fixed_part + lucky_number[mid:]
    elif position == "back":
        result = lucky_number + fixed_part
    else:
        raise ValueError("position 參數需為 'front'、'middle' 或 'back'")

    return result


def generate_multiple_lucky_numbers(magnetic_fields, total_length=8, count = 15, fixed_part="lucky", position="middle"):
    results = []
    for _ in range(count):
        result = generate_final_lucky_number(magnetic_fields, total_length, fixed_part, position)
        results.append(result)
    return results
