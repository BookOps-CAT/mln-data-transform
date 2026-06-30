def is_valid_isbn(isbn_str: str) -> bool:
    clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
    if len(clean_isbn) == 10:
        # First 9 characters must be numbers
        if not clean_isbn[:9].isdigit():
            return False

        # Calculate the weighted sum
        total = 0
        for i in range(9):
            total += int(clean_isbn[i]) * (10 - i)

        # Handle the check digit (can be a number or 'X' for 10)
        last_char = clean_isbn[9].upper()
        if last_char == "X":
            total += 10
        elif last_char.isdigit():
            total += int(last_char)
        else:
            return False

        return total % 11 == 0

    # 3. Process ISBN-13
    elif len(clean_isbn) == 13:
        if not clean_isbn.isdigit():
            return False

        # Alternating weights of 1 and 3
        total = 0
        for i in range(13):
            weight = 1 if i % 2 == 0 else 3
            total += int(clean_isbn[i]) * weight

        return total % 10 == 0

    return False


def normalize_isbn(isbn_str: str) -> str:
    clean_isbn = isbn_str.strip(".").replace("-", "").replace(" ", "")
    if len(clean_isbn) == 9:
        clean_isbn = f"0{clean_isbn}"
    return clean_isbn
