from datetime import datetime


def validate_date_string_format(value: str, expected_format: str = "%Y-%m-%d") -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    try:
        datetime.strptime(value, expected_format)
    except ValueError:
        raise ValueError(f"date must be in format {expected_format}")
    return value
