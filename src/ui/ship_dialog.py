from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QInputDialog,
    QMessageBox,
)

from database import (
    get_ship_categories,
    create_ship_category,
)


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
        self.add_category_button = QPushButton("Новая категория")
        self.add_category_button.clicked.connect(self.add_category)

        if category_id is not None:
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow("Модель:", self.model_input)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.add_category_button)

        form_layout.addRow("Категория:", category_layout)
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

        self.load_categories(selected_category_id=category_id)

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.model_input.text().strip(),
            self.category_combo.currentData(),
            self.scale_input.text().strip(),
        )
    
    def load_categories(self, selected_category_id=None):
        self.category_combo.clear()

        for row in get_ship_categories():
            category_id = row[0]
            name = row[1]

            self.category_combo.addItem(name, category_id)

        if selected_category_id is not None:
            index = self.category_combo.findData(selected_category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)


    def add_category(self):
        name, ok = QInputDialog.getText(
            self,
            "Новая категория",
            "Введите название категории:"
        )

        name = name.strip()

        if not ok or not name:
            return

        try:
            category_id = create_ship_category(name)
            self.load_categories(selected_category_id=category_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать категорию:\n\n{error}"
            )
