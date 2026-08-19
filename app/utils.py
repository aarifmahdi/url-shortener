def convert_to_base62(num: int) -> str:
    """
    num is a base 10 number.
    Returns a 4-character base62 string, zero-padded.
    Raises ValueError if num is too large to fit in 4 base62 characters.
    """
    lookup = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if num == 0:
        result = lookup[0]
    else:
        chars = []
        n = num
        while n != 0:
            remainder = n % 62
            chars.append(lookup[remainder])
            n //= 62
        chars.reverse()
        result = "".join(chars)

    if len(result) > 4:
        raise ValueError(f"id {num} exceeds max short_code capacity (62^4 combinations)")

    return result.zfill(4)