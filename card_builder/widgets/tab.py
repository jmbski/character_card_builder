"""Generic/base tab class structure"""

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QWidget

from card_builder.models import TabSchema
from card_builder.widgets import CardQtBase


class BaseTab(CardQtBase):
    """Tab for editing character card information with scrollable content."""

    def __init__(self, parent: QObject = None, schema: TabSchema = None) -> None:
        super().__init__(parent)

        self.schema: TabSchema = None
        self.title: str = ""
        self.value_paths: list[str] = []

        # Outer layout of the tab (contains the scroll area)
        outer_layout = QVBoxLayout(self)

        # Scroll area and scrollable widget
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        self.inner_layout = QVBoxLayout(scroll_widget)

        scroll_area.setWidget(scroll_widget)
        outer_layout.addWidget(scroll_area)
        self.layout = self.inner_layout
        if schema:
            self.schema = schema
            self.title = schema.tab_name
            self.value_paths = schema.value_paths

            for key, p_schema in schema.property_defs.items():
                widget = p_schema.widget
                if callable(widget):
                    widget = widget()
                    self.add_widget(key, widget, p_schema.label)
                else:
                    print(f"Invalid widget for {key}")
