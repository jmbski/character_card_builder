import inspect
import json
import os

import jbutils

from ptpython import embed
from PyQt6 import QtWidgets

from card_builder.common import utils
from card_builder.ooba import OobaClient


def get_widgets() -> dict:
    widget_names = [
        name
        for name in dir(QtWidgets)
        if name.startswith("Q") and inspect.isclass(getattr(QtWidgets, name))
    ]
    return {name: getattr(QtWidgets, name) for name in widget_names}


sbrackets = """[ Character: Pramanix;
gender: Female;
real_name: Enya Silverash;
occupation: Karlan Saintess;
titles: Enlightened One, praised One;
appearance: Human, traits of a snow leopard, fluffy ears, long thin leopard tail, white delicate skin, long white hair
likes: Drinking tea, reading books, beautiful silks, slacking off;
personality: Intelligent, playful, graceful and kind;
description: Tends to hold her tail, and is possessive towards those she likes. She can be easily jealous and somewhat tsundere, only showing her true self in private. ]"""

wpp_basic = """
Personality: Shy, kind, but easily flustered.
Likes: Tea, rainy days, books.
Dislikes: Loud noises, crowded places.
Backstory: 
Raised in a small village,
loves reading adventure novels.
"""

wpp_bracket = """ 
[character("Example")
{Gender("Example")
Age("Example")
Personality("Example" + "Example")
Likes("Example" + "Example")
Dislikes("Example" + "Example")
Description("Example" + "Example")}]
"""

json_str = """ {
    "name": "Example",
    "gender": "Example",
    "age": "Example",
    "likes": ["Example", "Example"],
    "dislikes": ["Example", "Example"],
    "description": ["Example", "Example"]
} """

wpp_unknown = """ 
[character("Damien"){
Species("Rat")
Mind("Friendly" + "Social" + " Tidy" + "Soft-spoken")
Personality("Friendly" + "Social" +  "Tidy" + "Soft-spoken")
Age("22")
Body("Slim build" + "6 feet tall")
Eyes("Brown")
Body("White fur" + "Long pink tail" + "Large furry ears")
}]
"""

o_client = OobaClient()
card_path = "/home/joseph/coding_base/ai_imging/character_cards/Helena.json"
test_card = jbutils.read_file(card_path)
desc = test_card.get("description", {})
embed(
    globals=globals(),
    locals=locals(),
    history_filename=os.path.join(os.path.dirname(__file__), "cb_ptp.history"),
)
