from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
)

from database.utils import make_short_name


class JudgeDialog(QDialog):
    def __init__(self, parent=None, full_name="", short_name=""):
        super().__init__(parent)

        self.setWindowTitle("Судья")

        self.full_name_input = QLineEdit()
        self.full_name_input.setText(full_name)

        self.short_name_input = QLineEdit()
        self.short_name_input.setText(short_name)

        self.full_name_input.textChanged.connect(self.update_short_name)

        form_layout = QFormLayout()
        form_layout.addRow("Полное ФИО:", self.full_name_input)
        form_layout.addRow("Краткое имя:", self.short_name_input)

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

    def update_short_name(self):
        self.short_name_input.setText(
            make_short_name(self.full_name_input.text())
        )

    def get_data(self):
        return (
            self.full_name_input.text().strip(),
            self.short_name_input.text().strip()
        )
