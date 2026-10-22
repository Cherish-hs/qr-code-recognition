# validators.py

from urllib.parse import urlparse
'''
检验EAN-13码是否有效，检验URL是否有效
'''

def is_valid_ean13(code):
    if len(code) != 13 or not code.isdigit():
        return False

    digits = [int(c) for c in code]

    total = sum(
        digits[i] for i in range(12)
        if i % 2 == 0
    )

    total += 3 * sum(
        digits[i] for i in range(12)
        if i % 2 == 1
    )

    check_digit = (10 - total % 10) % 10

    return check_digit == digits[12]


def get_valid_url(data):
    try:
        data = data.strip()
        parsed = urlparse(data)

        if (
            parsed.scheme in ("http", "https")
            and parsed.hostname
            and not any(c.isspace() for c in data)
        ):
            return data

    except ValueError:
        pass

    return None