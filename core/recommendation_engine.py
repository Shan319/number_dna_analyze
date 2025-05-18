import random

# 每種磁場對應的兩位數字組合
magneticic_pairs = {
    "伏位": ["11", "22", "33", "44", "66", "77", "88", "99"],
    "生氣": ["14", "41", "67", "76", "39", "93", "28", "82"],
    "天醫": ["13", "31", "68", "86", "49", "94", "27", "72"],
    "延年": ["19", "91", "78", "87", "34", "43", "26", "62"]
}

# 用於磁場抵銷的原始函式
def generate_lucky_numbers(magnetic_fields):
    fields = magnetic_fields.copy()
    neg_fields = dict()
    cancel_fields = {"天醫": 0, "生氣": 0, "伏位": 0, "延年": 0, "天醫+生氣+延年": 0}

    neg_fields["五鬼"] = fields.get("五鬼", 0)
    neg_fields["六煞"] = fields.get("六煞", 0)
    neg_fields["絕命"] = fields.get("絕命", 0)
    neg_fields["禍害"] = fields.get("禍害", 0)

    while neg_fields["絕命"] > 0:
        cancel_fields["天醫"] += 1
        neg_fields["絕命"] -= 1

    while neg_fields["六煞"] > 0:
        cancel_fields["延年"] += 1
        neg_fields["六煞"] -= 1

    while neg_fields["五鬼"] > 0:
        cancel_fields["天醫+生氣+延年"] += 1
        neg_fields["五鬼"] -= 1

    while neg_fields["禍害"] > 0:
        cancel_fields["生氣"] += 1
        r = random.sample(["生氣", "伏位", "延年"], k=1)[0]
        cancel_fields[r] += 1
        neg_fields["禍害"] -= 1

    return cancel_fields

def generate_lucky_number_chain_by_cancel_fields(cancel_fields, length):
    num_fields = length - 1
    magnetic_sequence = []

    # 將所有磁場對應的字典展平為 (field, pair) 的組合
    all_pairs_by_field = []
    for field in ["天醫", "生氣", "伏位", "延年"]:
        for pair in magneticic_pairs[field]:
            all_pairs_by_field.append((field, pair))

    # 儲存剩餘的 cancel_fields 數量
    remaining_fields = cancel_fields.copy()

    # 起始磁場：從有剩餘的 cancel_fields 中選
    possible_start_fields = [f for f in remaining_fields if remaining_fields[f] > 0]
    random.shuffle(possible_start_fields)
    for field in possible_start_fields:
        if remaining_fields[field] > 0:
            start_pair = random.choice(magneticic_pairs[field])
            magnetic_sequence.append(start_pair)
            remaining_fields[field] -= 1
            break

    # 開始接龍
    while len(magnetic_sequence) < num_fields:
        last_digit = magnetic_sequence[-1][1]

        # 找所有合法接得上的磁場對，且 cancel_fields 還有剩
        candidates = []
        for field in ["天醫", "生氣", "伏位", "延年"]:
            if remaining_fields.get(field, 0) > 0:
                for pair in magneticic_pairs[field]:
                    if pair[0] == last_digit:
                        candidates.append((field, pair))

        if not candidates:
            break  # 沒有可以接上的磁場對，結束

        field, pair = random.choice(candidates)
        magnetic_sequence.append(pair)
        remaining_fields[field] -= 1

    # 串接成幸運數字
    result = magnetic_sequence[0]
    for i in range(1, len(magnetic_sequence)):
        result += magnetic_sequence[i][1]

    return result


# 產生多組幸運數字（連續磁場模式）
def generate_multiple_lucky_numbers(magnetic_input, length, count=15):
    cancel = generate_lucky_numbers(magnetic_input)
    results = []
    for _ in range(count):
        lucky = generate_lucky_number_chain_by_cancel_fields(cancel, length)
        results.append(lucky)
    return results

