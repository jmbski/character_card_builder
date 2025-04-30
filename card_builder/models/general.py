"""Common general data model structures. May break out into smaller modules if needed"""

from dataclasses import dataclass, field
from typing import Any

import jbqt.widgets
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget


@dataclass
class PropertyDef:
    data_type: type = str
    default: Any = None
    label: str = ""
    widget: str | QWidget = None
    key: str = ""
    value_paths: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.widget, str):
            if hasattr(jbqt.widgets, self.widget):
                self.widget = getattr(jbqt.widgets, self.widget)
            elif hasattr(QtWidgets, self.widget):
                self.widget = getattr(QtWidgets, self.widget)
            else:
                raise TypeError(f"No widget type found matching for {self.widget}")

    def get_default(self) -> Any:
        value = None
        match self.data_type:
            case "int":
                value = 0
            case "float":
                value = 0.0
            case "bool":
                value = False
            case "list":
                value = []
            case "dict":
                value = {}
            case _:
                value = ""

        return self.default or value


@dataclass
class TabSchema:
    tab_name: str = ""
    property_defs: dict[str, PropertyDef | dict] = field(default_factory=dict)
    value_paths: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.property_defs:
            for key, value in self.property_defs.items():
                if isinstance(value, dict):
                    value = PropertyDef(**value)
                    self.property_defs[key] = value
                if not value.key:
                    value.key = key
