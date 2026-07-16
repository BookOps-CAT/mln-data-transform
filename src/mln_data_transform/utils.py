import re


def is_valid_isbn(isbn_str: str) -> bool:
    clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
    if len(clean_isbn) == 10:
        if not clean_isbn[:9].isdigit():
            return False

        total = 0
        for i in range(9):
            total += int(clean_isbn[i]) * (10 - i)

        last_char = clean_isbn[9].upper()
        if last_char == "X":
            total += 10
        elif last_char.isdigit():
            total += int(last_char)
        else:
            return False

        return total % 11 == 0

    elif len(clean_isbn) == 13:
        if not clean_isbn.isdigit():
            return False

        total = 0
        for i in range(13):
            weight = 1 if i % 2 == 0 else 3
            total += int(clean_isbn[i]) * weight

        return total % 10 == 0

    return False


def is_valid_upc(upc_str: str) -> bool:
    clean_upc = upc_str.strip(".").replace("-", "").replace(" ", "")
    if len(clean_upc) != 12 or not clean_upc.isdigit():
        return False

    total = 0
    for index in range(11):
        digit = int(clean_upc[index])
        total += digit * (3 if index % 2 == 0 else 1)

    check_digit = int(clean_upc[-1])
    return (total + check_digit) % 10 == 0


def normalize_isbn(isbn_str: str) -> str:
    clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
    if len(clean_isbn) == 9:
        clean_isbn = f"0{clean_isbn}"
    elif len(clean_isbn) == 12 and clean_isbn.startswith("78"):
        clean_isbn = f"9{clean_isbn}"
    return clean_isbn


def map_to_closest_grade_enum(grade_str: str) -> str | None:
    """Applies explicit overrides, then falls back to Euclidean distance."""
    clean_str = grade_str.strip(".")
    if clean_str in ["1-12", "k-12", "K-12"]:
        return "E"
    if clean_str.startswith(("0", "Pre")):
        return "A"
    if clean_str.startswith("K") or clean_str.endswith(("-2", "-3")):
        return "B"
    match = re.match(r"^(\d{1,2})\-(\d{1,2})$", clean_str)
    if not match:
        return None
    start, end = match.groups()
    start = int(start)
    end = int(end)
    best_match = None
    min_distance = float("inf")
    bounds = {"C": (3, 5), "D": (6, 8), "E": (9, 12)}
    for enum_val, (enum_start, enum_end) in bounds.items():
        distance = (start - enum_start) ** 2 + (end - enum_end) ** 2

        if distance < min_distance:
            min_distance = distance
            best_match = enum_val

    return best_match
