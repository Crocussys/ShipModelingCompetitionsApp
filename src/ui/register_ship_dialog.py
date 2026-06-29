from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)

from database import (
    get_registered_competition_teams,
    get_groups,
    get_registered_participants_for_combo,
)


class RegisterShipDialog(QDialog):
    def __init__(self, parent=None, competition_id=None):
        super().__init__(parent)

        self.competition_id = competition_id
        self.setWindowTitle("Регистрация судна")

        self.team_combo = QComboBox()
        self.group_combo = QComboBox()
        self.participant_combo = QComboBox()

        self.team_combo.currentIndexChanged.connect(self.load_participants)
        self.group_combo.currentIndexChanged.connect(self.load_participants)

        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Канал/частота")

        form_layout = QFormLayout()
        form_layout.addRow("Команда:", self.team_combo)
        form_layout.addRow("Группа:", self.group_combo)
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

        self.load_data()

    def validate_and_accept(self):
        if self.team_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Нет зарегистрированных команд")
            return

        if self.group_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Нет групп")
            return

        if self.participant_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нет участников для выбранной команды и группы"
            )
            return

        self.accept()

    def get_data(self):
        return (
            self.participant_combo.currentData(),
            self.channel_input.text().strip(),
        )
    
    def load_data(self):
        self.load_teams()
        self.load_groups()
        self.load_participants()


    def load_teams(self):
        self.team_combo.clear()

        for competition_team_id, short_name in get_registered_competition_teams(
            self.competition_id
        ):
            self.team_combo.addItem(short_name, competition_team_id)


    def load_groups(self):
        self.group_combo.clear()

        for group_id, name in get_groups():
            self.group_combo.addItem(name, group_id)


    def load_participants(self):
        self.participant_combo.clear()

        competition_team_id = self.team_combo.currentData()
        group_id = self.group_combo.currentData()

        if competition_team_id is None or group_id is None:
            return

        for competition_team_participant_id, full_name in get_registered_participants_for_combo(
            self.competition_id,
            competition_team_id=competition_team_id,
            group_id=group_id,
        ):
            self.participant_combo.addItem(full_name, competition_team_participant_id)
