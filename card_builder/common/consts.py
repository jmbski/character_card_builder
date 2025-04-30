"""card builder app constants"""

import jbutils

from card_builder.models import PropertyDef, TabSchema

# TODO: update with an automated config reader feature
CFG_PATH = "/home/joseph/coding_base/ai_imging/.cb_cfg.yaml"

DATA_FIELDS: list[str] = [
    "name",
    "description",
    "personality",
    "first_mes",
    "avatar",
    "mes_example",
    "scenario",
    "creator_notes",
    "system_prompt",
    "post_history_instructions",
    "alternate_greetings",
    "tags",
    "creator",
    "character_version",
    "extensions",
    "group_only_greetings",
]
""" Fields that go inside the nested 'data' property of the card """

CB_CFG: dict = jbutils.read_file(CFG_PATH) or {}

TAB_SCHEMAS: list[TabSchema] = [
    TabSchema(**schema) for schema in CB_CFG.get("tabs", [])
]


class CbGlobals:
    OOBA_API_URL = "http://localhost:5000/v1/completions"
    CARDS_DIR = "/home/joseph/coding_base/ai_imging/character_cards"


class TABS:
    CARD_META = "Card Meta Data"
    DESCRIPTION = "Description"
    PERSONALITY = "Personality"
    SCENARIO = "Scenario"
    FIRST_MESSAGE = "First Message"
    SYSTEM_PROMP = "System Prompt"
    POST_HISTORY = "Post History Instructions"
