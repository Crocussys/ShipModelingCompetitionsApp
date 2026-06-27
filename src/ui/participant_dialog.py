from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDateEdit,
    QDialogButtonBox,
)


class ParticipantDialog(QDialog):
    def __init__(self, parent=None, full_name="", birth_date=""):
        super().__init__(parent)

        self.setWindowTitle("Участник")

        self.full_name_input = QLineEdit(full_name)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDisplayFormat("dd.MM.yyyy")

        if birth_date:
            date = QDate.fromString(birth_date, "yyyy-MM-dd")
            self.birth_date_input.setDate(date)
        else:
            self.birth_date_input.setDate(QDate.currentDate())

        form_layout = QFormLayout()
        form_layout.addRow("ФИО:", self.full_name_input)
        form_layout.addRow("Дата рождения:", self.birth_date_input)

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
            self.full_name_input.text().strip(),
            self.birth_date_input.date().toString("yyyy-MM-dd"),
        )
