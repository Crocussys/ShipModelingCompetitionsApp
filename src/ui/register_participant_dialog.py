from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
)

from database import (
    get_groups,
    get_registered_competition_teams,
)


class RegisterParticipantDialog(QDialog):
    def __init__(self, parent=None, competition_id=None):
        super().__init__(parent)

        self.competition_id = competition_id

        self.setWindowTitle("Регистрация участника")

        self.team_combo = QComboBox()
        self.group_combo = QComboBox()

        form_layout = QFormLayout()
        form_layout.addRow("Команда:", self.team_combo)
        form_layout.addRow("Группа:", self.group_combo)

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

        self.load_data()

    def load_data(self):
        self.team_combo.clear()
        self.group_combo.clear()

        teams = get_registered_competition_teams(self.competition_id)
        groups = get_groups()

        for competition_team_id, short_name in teams:
            self.team_combo.addItem(short_name, competition_team_id)

        for group_id, name in groups:
            self.group_combo.addItem(name, group_id)

    def validate_and_accept(self):
        if self.team_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Нет зарегистрированных команд")
            return

        if self.group_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Нет групп")
            return

        self.accept()

    def get_data(self):
        return (
            self.team_combo.currentData(),
            self.group_combo.currentData(),
        )
