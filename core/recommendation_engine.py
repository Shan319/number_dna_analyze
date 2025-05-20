import random
import string

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
def generate_lucky_number(cancel_fields, length, num_triplets):
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

    if not magnetic_sequence:
        return ""
    result = magnetic_sequence[0]
    for i in range(1, len(magnetic_sequence)):
        result += magnetic_sequence[i][1]

    return result

def generate_two_random_letters():
    return ''.join(random.sample(string.ascii_lowercase, 2))

def insert_letters(num_str, letters, position):
    if position == "front":
        return letters + num_str
    elif position == "middle":
        mid = len(num_str) // 2
        return num_str[:mid] + letters + num_str[mid:]
    elif position == "back":
        return num_str + letters
    else:
        return num_str

def generate_multiple_lucky_numbers(magnetic_input, total_length, count=15, alphanumeric=False, letter_pos="back", fixed_part=""):
    cancel, wugui_triplets = cancel_negative_magnetic_field(magnetic_input)
    results = []

    is_fixed_alpha = fixed_part.isalpha()
    is_fixed_digit = fixed_part.isdigit()
    fixed_len = len(fixed_part)

    for _ in range(count):
        if not alphanumeric:
            if not fixed_part:
                lucky = generate_lucky_number(cancel, total_length, wugui_triplets)
                results.append(lucky)
            elif is_fixed_digit:
                remain_len = total_length - fixed_len
                lucky = generate_lucky_number(cancel, remain_len, wugui_triplets)
                results.append(fixed_part + lucky)

        else:
            if not fixed_part:
                letters = generate_two_random_letters()
                num_len = total_length - 2
                lucky = generate_lucky_number(cancel, num_len, wugui_triplets)
                results.append(insert_letters(lucky, letters, letter_pos))

            elif is_fixed_alpha:
                num_len = total_length - fixed_len
                lucky = generate_lucky_number(cancel, num_len, wugui_triplets)
                results.append(insert_letters(lucky, fixed_part, letter_pos))

            elif is_fixed_digit:
                num_len = total_length - fixed_len
                letters = generate_two_random_letters()
                lucky = generate_lucky_number(cancel, num_len - 2, wugui_triplets)
                results.append(fixed_part + insert_letters(lucky, letters, letter_pos))

    return results
