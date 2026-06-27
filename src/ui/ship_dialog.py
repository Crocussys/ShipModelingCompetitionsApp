from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
)

from database import get_ship_categories


class ShipDialog(QDialog):
    def __init__(
        self,
        parent=None,
        name="",
        model="",
        category_id=None,
        scale="",
    ):
        super().__init__(parent)

        self.setWindowTitle("Судно")

        self.name_input = QLineEdit(name)
        self.model_input = QLineEdit(model)
        self.scale_input = QLineEdit(scale)

        self.category_combo = QComboBox()

        for current_category_id, category_name in get_ship_categories():
            self.category_combo.addItem(category_name, current_category_id)

        if category_id is not None:
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow("Модель:", self.model_input)
        form_layout.addRow("Категория:", self.category_combo)
        form_layout.addRow("Масштаб:", self.scale_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.model_input.text().strip(),
            self.category_combo.currentData(),
            self.scale_input.text().strip(),
        )
