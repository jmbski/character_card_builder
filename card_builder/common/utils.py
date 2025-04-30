import json
import re

import jbutils

from card_builder.common import consts, TABS
from card_builder.ooba import OobaClient


def get_tab(tab_id: str | TABS):
    for tab in consts.TAB_SCHEMAS:
        if tab.tab_name == tab_id:
            return tab


def detect_format(input_text: str) -> str:
    """Detects the format of the input text.

    Args:
        input_text (str): The input string to analyze.

    Returns:
        str: The detected format. One of 'json', 'wpp_basic', 'wpp_bracket', 'square_bracket', or 'plain'.
    """
    try:
        json.loads(input_text)
        return "json"
    except (json.JSONDecodeError, TypeError):
        pass

    if re.search(r"^\s*\[.*?:.*?;.*?\]\s*$", input_text, re.DOTALL):
        return "square_bracket"

    if re.search(r"^\s*(?:\w+|\[.*?\]|\(.*?\))\s*:\s*.+", input_text, re.MULTILINE):
        # Handles w++ basic and w++ bracket style
        if re.search(r"^\s*[\[\(].*?[\]\)]\s*:", input_text, re.MULTILINE):
            return "wpp_bracket"
        return "wpp_basic"

    return "plain"


def parse_json(input_text: str) -> dict[str, str]:
    """Parses a JSON-formatted string into a dictionary."""
    return json.loads(input_text)


def parse_wpp_basic(input_text: str) -> dict[str, str]:
    """Parses a basic w++-formatted string into a dictionary."""
    result: dict[str, str] = {}
    current_key: str | None = None
    current_value_lines: list[str] = []

    for line in input_text.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if ":" in stripped_line:
            if current_key:
                result[current_key] = " ".join(current_value_lines).strip()

            key, value = stripped_line.split(":", 1)
            current_key = key.strip()
            current_value_lines = [value.strip()]
        else:
            if current_key:
                current_value_lines.append(stripped_line)

    if current_key:
        result[current_key] = " ".join(current_value_lines).strip()

    return result


def parse_wpp_bracket(input_text: str) -> dict[str, str]:
    """Parses a w++-bracket formatted string into a dictionary.

    Example:
        [Likes]: Reading, quiet places.
        (Personality): Curious, analytical.
    """
    result: dict[str, str] = {}
    for line in input_text.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        match = re.match(r"^[\[\(](.*?)[\]\)]\s*:\s*(.+)$", stripped_line)
        if match:
            key, value = match.groups()
            result[key.strip()] = value.strip()

    return result


def parse_square_bracket(input_text: str) -> dict[str, str]:
    """Parses a 'square bracket' single-line format into a dictionary.

    Example:
        [Key1: Value1; Key2: Value2]
    """
    result: dict[str, str] = {}
    content = input_text.strip().lstrip("[").rstrip("]")
    pairs = content.split(";")
    for pair in pairs:
        if ":" in pair:
            key, value = pair.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def parse_plain(input_text: str, fields: list[str] = None) -> dict[str, str]:
    """Fallback parser for plain text. Returns empty dictionary."""
    client = OobaClient()
    return client.parse_character_card(input_text, fields)


def parse_character_card(
    input_text: str, fields: list[str] = None
) -> dict[str, str]:
    """Parses a character card string into a dictionary based on detected format.

    Args:
        input_text (str): The raw character card string.

    Returns:
        dict[str, str]: Parsed key-value pairs.
    """
    if isinstance(input_text, dict):
        return input_text
    format_type = detect_format(input_text)
    print(f"formatting for type: {format_type}")
    if format_type == "json":
        return parse_json(input_text)
    elif format_type == "wpp_basic":
        return parse_wpp_basic(input_text)
    elif format_type == "wpp_bracket":
        return parse_wpp_bracket(input_text)
    elif format_type == "square_bracket":
        return parse_square_bracket(input_text)
    else:
        return parse_plain(input_text, fields)
