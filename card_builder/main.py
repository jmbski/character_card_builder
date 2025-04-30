import json
import logging
import logging.config
import os
import jbqt.common
import jbqt.common.consts
import jbqt.widgets
import requests
import sys

from typing import Optional

import jbutils

from jbqt.common import GlobalRefs, register_app, qt_utils
from jbqt.widgets import ChipsWidget
from jbqt.dialogs import JbFileDialog, InputDialog

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QCalendarWidget,
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTabWidget,
    QListWidget,
    QMessageBox,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QLayout,
)
from PyQt6.QtCore import Qt, QObject

from card_builder.common import consts, utils, CbGlobals
from card_builder.ooba import OobaClient
from card_builder.ooba import client
from card_builder.widgets import CardQtBase, BaseTab

DATA_DIR = "./cards"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DESCRIPTION_TEMPLATE: dict[str, str] = {
    "Character": "",
    "Age": "",
    "Gender": "",
    "Pronouns": "",
    "Appearance": "",
    "Role/Occupation": "",
    "Specials/Race": "Human",
    "Speech Style": "",
    "Extra Info": "",
    "General Behavior": "",
    "Inventory": "",
    "Response Guidance": "",
}

PERSONALITY_TEMPLATE: dict[str, str] = {
    "Personality Traits": "",
    "Emotional Disposition": "",
    "Attitude towards {{user}}": "",
    "Hates": "",
    "Dislikes": "",
    "Likes": "",
    "Loves": "",
    "Goals": "",
    "Fears": "",
}

CARD_TEMPLATE: dict = {
    "name": "",
    "description": "",
    "personality": "",
    "scenario": "",
    "first_mes": "",
    "mes_example": "",
    "creatorcomment": "",
    "avatar": "",
    "chat": "",
    "talkativeness": "",
    "fav": False,
    "tags": [],
    "spec": "chara_card_v3",
    "spec_version": "3.0",
    "data": {
        "name": "",
        "description": "",
        "personality": "",
        "avatar": "none",
        "scenario": "",
        "first_mes": "",
        "mes_example": "",
        "creator_notes": "",
        "system_prompt": "",
        "post_history_instructions": "",
        "tags": [],
        "creator": "",
        "character_version": "main",
        "alternate_greetings": [],
        "extensions": {
            "talkativeness": "",
            "fav": False,
            "world": "",
            "depth_prompt": {"prompt": "", "depth": "", "role": ""},
        },
        "group_only_greetings": [],
    },
    "create_date": "",
}


class FormatterProfile:
    """Holds settings for formatting generated messages."""

    def __init__(self) -> None:
        self.speech_style: str = "Quotes"
        self.perspective: str = "First Person"
        self.user_reference: str = "you"


class AlternatGreetingsTab(CardQtBase):
    def __init__(self, parent=None, layout=None, default_labels=True):
        super().__init__(parent, layout, default_labels)
        self.layout = QVBoxLayout(self)


class GroupOnlyGreetTab(CardQtBase):
    def __init__(self, parent=None, layout=None, default_labels=True):
        super().__init__(parent, layout, default_labels)
        self.layout = QVBoxLayout(self)


class MessageGenTab(CardQtBase):
    """Tab for generating example messages using OobaClient."""

    def __init__(self, editor_tab=None, parent: QObject = None) -> None:
        super().__init__(parent)
        self.editor_tab = editor_tab
        self.client = OobaClient()

        self.layout = QVBoxLayout(self)

        self.prompt_editor = QTextEdit()
        self.temperature_box = QDoubleSpinBox()
        self.temperature_box.setRange(0.1, 2.0)
        self.temperature_box.setSingleStep(0.1)
        self.temperature_box.setValue(0.7)

        self.max_tokens_box = QSpinBox()
        self.max_tokens_box.setRange(10, 1024)
        self.max_tokens_box.setValue(200)

        self.output_list = QListWidget()

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.layout.addWidget(QLabel("Prompt"))
        self.layout.addWidget(self.prompt_editor)

        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Temperature"))
        settings_layout.addWidget(self.temperature_box)
        settings_layout.addWidget(QLabel("Max New Tokens"))
        settings_layout.addWidget(self.max_tokens_box)

        self.layout.addLayout(settings_layout)

        gen_button = QPushButton("Generate")
        gen_button.clicked.connect(self.generate_message)
        self.layout.addWidget(gen_button)

        self.layout.addWidget(QLabel("Generated Outputs"))
        self.layout.addWidget(self.output_list)

        add_button = QPushButton("Add Selected to Example Messages")
        add_button.clicked.connect(self.add_selected)
        self.layout.addWidget(add_button)

    def generate_message(self) -> None:
        prompt = self.prompt_editor.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(
                self, "Missing Prompt", "Enter a prompt to generate."
            )
            return
        temp = self.temperature_box.value()
        tokens = self.max_tokens_box.value()
        result = self.client.generate(prompt, temp, tokens)
        if result:
            self.output_list.addItem(result.strip())
        else:
            QMessageBox.warning(
                self,
                "Generation Failed",
                "Failed to get a response from the server.",
            )

    def add_selected(self) -> None:
        selected = self.output_list.currentItem()
        if selected:
            self.editor_tab.mes_example_list.addItem(selected.text())


class MainWindow(QMainWindow):
    """Main window containing all tabs."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SillyTavern Card Builder")
        # self.setGeometry(200, 200, 500, 200)
        self.move(200, 200)
        self.use_ai_scan: QCheckBox = None

        """ self.tabs = QTabWidget()
        self.tab_refs = {
            schema.tab_name: BaseTab(self, schema) for schema in consts.TAB_SCHEMAS
        }

        for key, value in self.tab_refs.items():
            self.tabs.addTab(value, key) """

        ###
        self.tabs = QTabWidget()

        self.tab_refs = {
            schema.tab_name: BaseTab(self, schema) for schema in consts.TAB_SCHEMAS
        }
        for key, value in self.tab_refs.items():
            self.tabs.addTab(value, key)

        # Simple layout with tabs + buttons (no scroll area)
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tabs)
        self._setup_ui()

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        self.resize(1500, 1200)

    def _setup_ui(self) -> None:

        button_row = QHBoxLayout()
        save_button = QPushButton("Save Card")
        save_button.clicked.connect(self.open_save_dialog)
        new_button = QPushButton("New Card")
        new_button.clicked.connect(self.new_card)
        load_button = QPushButton("Load Card")
        load_button.clicked.connect(self.open_file)
        print_button = QPushButton("Print Card JSON")
        print_button.clicked.connect(self.print_card)
        self.use_ai_scan = QCheckBox("Scan w/ AI")

        button_row.addWidget(new_button)
        button_row.addWidget(save_button)
        button_row.addWidget(self.use_ai_scan)
        button_row.addWidget(load_button)
        button_row.addWidget(print_button)

        self.main_layout.addLayout(button_row)

    def get_card_data(self) -> dict:
        data = {}
        for tab in self.tab_refs.values():
            tab_data = tab.get_data()
            if tab.value_paths:
                for tab_path in tab.value_paths:
                    jbutils.set_nested(data, tab_path, json.dumps(tab_data))
            else:
                for key, value in tab_data.items():
                    schema = tab.schema.property_defs.get(key)
                    if not schema:
                        continue
                    if schema.value_paths:
                        for p_path in schema.value_paths:
                            jbutils.set_nested(data, p_path, value)
        return data

    def open_save_dialog(self) -> None:
        dialog = JbFileDialog("Save File", CbGlobals.CARDS_DIR, mode="save")
        dialog.selectedFile.connect(self.save_file)
        dialog.open_file_dialog()

    def save_file(self, path: str) -> None:

        data = self.get_card_data()

        jbutils.write_file(path, data)

    def open_file(self) -> None:

        file_dialog = JbFileDialog(
            title="Select Character Card",
            directory=CbGlobals.CARDS_DIR,
        )
        file_dialog.selectedFile.connect(self.load_card)

        file_dialog.open_file_dialog()

    def load_data(self, data: dict, use_ai: bool = True) -> None:
        sub_data = data.get("data")
        if isinstance(sub_data, dict):
            data.update(sub_data)
        desc = data.get("description")
        pers = data.get("personality")

        ooba_client = OobaClient()
        desc_json = {}
        pers_json = {}

        if desc:
            if isinstance(desc, str):
                resp = (
                    ooba_client.parse_character_card(desc)
                    if use_ai
                    else utils.parse_character_card(desc)
                )

                if resp and isinstance(resp, dict):
                    desc_json = resp.get("description", {}) if use_ai else resp
                    pers_json = resp.get("personality")
                    data["description"] = desc_json
            elif isinstance(desc, dict):
                data["description"] = desc
        if pers:
            if isinstance(pers, str):
                resp = (
                    ooba_client.parse_character_card(pers)
                    if use_ai
                    else utils.parse_character_card(pers)
                )
                if resp and isinstance(resp, dict):
                    resp_json = resp.get("personality", {}) if use_ai else resp
                    if pers_json and isinstance(pers_json, dict):
                        pers_json.update(resp_json)
                    else:
                        pers_json = resp_json
                        data["personality"] = pers_json
            elif isinstance(pers, dict):
                data["personality"] = pers
        for tab in self.tab_refs.values():

            if tab.title == "Description" and desc:
                tab_data = {
                    key: data["description"].pop(key)
                    for key in tab.widgets.keys()
                    if key in data["description"]
                }
                print("Desc data", data["description"])
            elif tab.title == "Personality" and pers:
                tab_data = {
                    key: data["personality"].pop(key)
                    for key in tab.widgets.keys()
                    if key in data["personality"]
                }
                print("Pers data", data["personality"])
            else:
                tab_data = {
                    key: data.pop(key) for key in tab.widgets.keys() if key in data
                }
            tab.set_data(tab_data)
        print(f"Unassigned keys: {list(data.keys())}")

    def load_card(self, filepath: str) -> None:
        if filepath.endswith(".json") or filepath.endswith(".yaml"):
            data = jbutils.read_file(filepath)
            if not isinstance(data, dict):
                return
            self.load_data(data, use_ai=self.use_ai_scan.isChecked())

    def new_card(self) -> None:

        data = client.get_blank_card()
        self.load_data(data, False)

    def print_card(self) -> None:
        data = self.get_card_data()
        jbutils.write_file("test.json", data)


if __name__ == "__main__":
    print(isinstance(Qt.CheckState.Checked, Qt.CheckState))
    app = QApplication(sys.argv)
    register_app(
        app, "/home/joseph/coding_base/ai_imging/prompter/prompter/images/icons"
    )
    window = MainWindow()
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec())
