from jbqt import qt_utils
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QLayout, QWidget, QVBoxLayout, QLabel


class CardQtBase(QWidget):
    def __init__(
        self,
        parent: QObject = None,
        layout: QLayout = None,
        default_labels: bool = True,
    ) -> None:
        super().__init__(parent)

        self.widgets: dict[str, QWidget] = {}
        self.labels: dict[str, QLabel] = {}
        self.layout = layout or QVBoxLayout()
        self.default_labels = default_labels

    def add_widget(self, name: str, widget: QWidget, label: str = "") -> None:
        """Adds a widget (and optional label) to the main layout and stores references.

        Args:
            name (str): Unique name for the widget.
            widget (QWidget): The widget instance to add.
            label (Optional[str]): Optional text for a QLabel placed above the widget.
        """
        if self.default_labels:
            label = name.title().replace("_", " ")

        if name not in self.widgets:
            self.widgets[name] = widget
            if label:
                self.labels[name] = QLabel(label)
                self.layout.addWidget(self.labels[name])
            self.layout.addWidget(widget)

    def add_label(self, name: str, label: str) -> None:
        """Inserts a label above an existing widget.

        Args:
            name (str): Name of the widget to associate the label with.
            label (str): The text to display in the new label.
        """
        widget = self.widgets.get(name)
        if widget is None:
            # TODO: add logging
            print(f"No widget found with name '{name}'")

        lbl = QLabel(label)

        # Find the index of the widget
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget() is widget:
                self.layout.insertWidget(i, lbl)
                self.labels[name] = lbl
                return

        # TODO: add logging
        print(f"Widget name: {name} not found in layout")

    def update_label(self, name: str, label: str) -> None:
        label_widget = self.labels.get(name)
        if label_widget:
            label_widget.setText(label)

    def update_widget(self, name: str, widget: QWidget) -> None:
        if name in self.widgets:
            self.del_widget(name)
        self.add_widget(name, widget)

    def del_widget(self, name: str | QWidget) -> None:
        widget: QWidget = None
        if isinstance(name, str):
            widget = self.widgets.get(name)
        elif isinstance(name, QWidget):
            for key, value in self.widgets.items():
                if value == name:
                    name = key
                    widget = value
                    break
        if not widget:
            return

        widget.deleteLater()
        # TODO: may need to change to just setting to None
        del self.widgets[name]

    def get_widgets(self) -> list[QWidget]:
        return list(self.widgets.values())

    def get_data(self) -> dict:
        data = {}
        for key, widget in self.widgets.items():
            data[key] = qt_utils.get_widget_value(widget, key)

        return data

    def set_data(self, data: dict) -> dict:
        if isinstance(data, str):
            print(data)
        for key, value in data.items():
            widget = self.widgets.get(key)
            if not widget:
                # TODO: logging
                print(f"No widget found for {key}")
                continue
            qt_utils.set_widget_value(widget, value)
