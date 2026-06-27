from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)

from database import get_registered_participants_for_combo


class RegisterShipDialog(QDialog):
    def __init__(self, parent=None, competition_id=None):
        super().__init__(parent)

        self.competition_id = competition_id
        self.setWindowTitle("Регистрация судна")

        self.participant_combo = QComboBox()
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Канал/частота")

        for ctp_id, display_text in get_registered_participants_for_combo(competition_id):
            self.participant_combo.addItem(display_text, ctp_id)

        form_layout = QFormLayout()
        form_layout.addRow("Участник:", self.participant_combo)
        form_layout.addRow("Канал/частота:", self.channel_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate_and_accept(self):
        if self.participant_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нет зарегистрированных участников"
            )
            return

        self.accept()

    def get_data(self):
        return (
            self.participant_combo.currentData(),
            self.channel_input.text().strip(),
        )
