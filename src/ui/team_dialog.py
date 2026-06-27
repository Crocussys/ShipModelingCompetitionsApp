from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QInputDialog,
    QDialogButtonBox,
    QMessageBox,
)

from database import (
    get_districts,
    create_district,
)


class TeamDialog(QDialog):
    def __init__(
        self,
        parent=None,
        short_name="",
        organization="",
        district_id=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Команда")

        self.short_name_input = QLineEdit(short_name)
        self.organization_input = QLineEdit(organization)

        self.district_combo = QComboBox()
        self.add_district_button = QPushButton("Новый район")

        self.add_district_button.clicked.connect(self.add_district)

        district_layout = QHBoxLayout()
        district_layout.addWidget(self.district_combo)
        district_layout.addWidget(self.add_district_button)

        form_layout = QFormLayout()
        form_layout.addRow("Короткое название:", self.short_name_input)
        form_layout.addRow("Организация:", self.organization_input)
        form_layout.addRow("Район:", district_layout)

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

        self.load_districts(selected_district_id=district_id)

    def load_districts(self, selected_district_id=None):
        self.district_combo.clear()

        districts = get_districts()

        for district_id, name in districts:
            self.district_combo.addItem(name, district_id)

        if selected_district_id is not None:
            index = self.district_combo.findData(selected_district_id)
            if index >= 0:
                self.district_combo.setCurrentIndex(index)

    def add_district(self):
        name, ok = QInputDialog.getText(
            self,
            "Новый район",
            "Введите название района/города:"
        )

        name = name.strip()

        if not ok or not name:
            return

        try:
            district_id = create_district(name)
            self.load_districts(selected_district_id=district_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить район:\n\n{error}"
            )

    def get_data(self):
        return (
            self.short_name_input.text().strip(),
            self.organization_input.text().strip(),
            self.district_combo.currentData(),
        )
