import re


def camel_case_to_snake_case(string: str) -> str:
    return "_".join(re.sub(r"([A-Z])", r" \1", string).lower().split())
