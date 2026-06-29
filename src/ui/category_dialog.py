from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QDialogButtonBox,
)


class CategoryDialog(QDialog):
    def __init__(
        self,
        parent=None,
        name="",
        protocol_1=False,
        protocol_2=False,
        protocol_3=False,
    ):
        super().__init__(parent)

        self.setWindowTitle("Категория")

        self.name_input = QLineEdit(name)

        self.protocol_1_checkbox = QCheckBox("Протокол №1")
        self.protocol_2_checkbox = QCheckBox("Протокол №2")
        self.protocol_3_checkbox = QCheckBox("Протокол №3")

        self.protocol_1_checkbox.setChecked(bool(protocol_1))
        self.protocol_2_checkbox.setChecked(bool(protocol_2))
        self.protocol_3_checkbox.setChecked(bool(protocol_3))

        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow(self.protocol_1_checkbox)
        form_layout.addRow(self.protocol_2_checkbox)
        form_layout.addRow(self.protocol_3_checkbox)

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
            self.protocol_1_checkbox.isChecked(),
            self.protocol_2_checkbox.isChecked(),
            self.protocol_3_checkbox.isChecked(),
        )
