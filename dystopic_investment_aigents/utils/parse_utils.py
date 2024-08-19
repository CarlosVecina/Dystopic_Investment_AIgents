import re


def camel_case_to_snake_case(string):
    return "_".join(re.sub( r"([A-Z])", r" \1", string).lower().split())