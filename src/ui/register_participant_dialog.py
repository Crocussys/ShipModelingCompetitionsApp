from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
    QHBoxLayout,
    QPushButton,
    QInputDialog,
)

from database import (
    get_groups,
    get_registered_competition_teams,
    create_group,
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
        
        self.add_group_button = QPushButton("Новая группа")
        self.add_group_button.clicked.connect(self.add_group)

        group_layout = QHBoxLayout()
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(self.add_group_button)

        form_layout.addRow("Группа:", group_layout)

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

        self.load_teams()
        self.load_groups()

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
    
    def load_teams(self):
        self.team_combo.clear()

        for competition_team_id, short_name in get_registered_competition_teams(
            self.competition_id
        ):
            self.team_combo.addItem(short_name, competition_team_id)
    
    def load_groups(self, selected_group_id=None):
        self.group_combo.clear()

        for group_id, name in get_groups():
            self.group_combo.addItem(name, group_id)

        if selected_group_id is not None:
            index = self.group_combo.findData(selected_group_id)
            if index >= 0:
                self.group_combo.setCurrentIndex(index)


    def add_group(self):
        name, ok = QInputDialog.getText(
            self,
            "Новая группа",
            "Введите название группы:"
        )

        name = name.strip()

        if not ok or not name:
            return

        try:
            group_id = create_group(name)
            self.load_groups(selected_group_id=group_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать группу:\n\n{error}"
            )
