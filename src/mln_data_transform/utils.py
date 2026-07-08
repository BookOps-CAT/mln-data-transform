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
    return clean_isbn
