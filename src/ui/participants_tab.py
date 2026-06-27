from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QComboBox,
    QCheckBox,
)

from database import (
    get_participants,
    get_competition_participants,
    create_participant,
    update_participant,
    delete_participant,
    is_participant_registered,
    register_participant,
    remove_participant_registration,
    get_groups,
    get_registered_competition_teams,
)

from ui.participant_dialog import ParticipantDialog
from ui.register_participant_dialog import RegisterParticipantDialog


class ParticipantsTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.show_registered_radio = QRadioButton("Участники этого соревнования")
        self.show_all_radio = QRadioButton("Все участники")
        self.show_registered_radio.setChecked(True)

        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.show_registered_radio)
        self.filter_group.addButton(self.show_all_radio)

        self.show_registered_radio.toggled.connect(self.update_mode)
        self.show_all_radio.toggled.connect(self.update_mode)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО")
        self.search_input.textChanged.connect(self.load_participants)

        self.group_filter_checkbox = QCheckBox("Группа")
        self.group_filter_combo = QComboBox()

        self.team_filter_checkbox = QCheckBox("Команда")
        self.team_filter_combo = QComboBox()

        self.group_filter_checkbox.toggled.connect(self.load_participants)
        self.team_filter_checkbox.toggled.connect(self.load_participants)
        self.group_filter_combo.currentIndexChanged.connect(self.load_participants)
        self.team_filter_combo.currentIndexChanged.connect(self.load_participants)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.register_button = QPushButton("Зарегистрировать участника")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.remove_button = QPushButton("Убрать из соревнования")

        self.register_button.clicked.connect(self.register_selected_participant)
        self.add_button.clicked.connect(self.add_participant)
        self.edit_button.clicked.connect(self.edit_selected_participant)
        self.delete_button.clicked.connect(self.delete_selected_participant)
        self.remove_button.clicked.connect(self.remove_selected_registration)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.show_registered_radio)
        mode_layout.addWidget(self.show_all_radio)
        mode_layout.addStretch()

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.group_filter_checkbox)
        filters_layout.addWidget(self.group_filter_combo)
        filters_layout.addWidget(self.team_filter_checkbox)
        filters_layout.addWidget(self.team_filter_combo)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.register_button)
        actions_layout.addWidget(self.add_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addWidget(self.remove_button)
        actions_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(mode_layout)
        layout.addLayout(filters_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_filter_values()
        self.update_mode()

    def reset_mode(self):
        self.show_registered_radio.setChecked(True)
        self.update_mode()

    def update_mode(self):
        registered_mode = self.show_registered_radio.isChecked()

        self.register_button.setVisible(not registered_mode)
        self.add_button.setVisible(not registered_mode)
        self.edit_button.setVisible(not registered_mode)
        self.delete_button.setVisible(not registered_mode)

        self.remove_button.setVisible(registered_mode)

        self.group_filter_checkbox.setVisible(registered_mode)
        self.group_filter_combo.setVisible(registered_mode)
        self.team_filter_checkbox.setVisible(registered_mode)
        self.team_filter_combo.setVisible(registered_mode)

        self.load_filter_values()
        self.load_participants()

    def load_filter_values(self):
        self.group_filter_combo.blockSignals(True)
        self.team_filter_combo.blockSignals(True)

        self.group_filter_combo.clear()
        self.team_filter_combo.clear()

        for group_id, name in get_groups():
            self.group_filter_combo.addItem(name, group_id)

        for competition_team_id, short_name in get_registered_competition_teams(
            self.app_window.selected_competition_id
        ):
            self.team_filter_combo.addItem(short_name, competition_team_id)

        self.group_filter_combo.blockSignals(False)
        self.team_filter_combo.blockSignals(False)

    def load_participants(self):
        search = self.search_input.text()
        competition_id = self.app_window.selected_competition_id

        if self.show_all_radio.isChecked():
            participants = get_participants(search=search)

            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Участвует",
                "ФИО",
                "Дата рождения",
            ])

            self.table.setRowCount(len(participants))

            for row_index, (participant_id, full_name, birth_date) in enumerate(participants):
                registered = is_participant_registered(
                    participant_id,
                    competition_id,
                )

                self.table.setItem(row_index, 0, QTableWidgetItem(str(participant_id)))
                self.table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem("Да" if registered else "Нет")
                )
                self.table.setItem(row_index, 2, QTableWidgetItem(full_name))
                self.table.setItem(
                    row_index,
                    3,
                    QTableWidgetItem(self.format_date_for_ui(birth_date))
                )

        else:
            group_id = None
            competition_team_id = None

            if self.group_filter_checkbox.isChecked():
                group_id = self.group_filter_combo.currentData()

            if self.team_filter_checkbox.isChecked():
                competition_team_id = self.team_filter_combo.currentData()

            rows = get_competition_participants(
                competition_id=competition_id,
                search=search,
                group_id=group_id,
                competition_team_id=competition_team_id,
            )

            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "ID регистрации",
                "ID",
                "ФИО",
                "Дата рождения",
                "Группа",
                "Команда",
            ])

            self.table.setRowCount(len(rows))

            for row_index, (
                registration_id,
                participant_id,
                full_name,
                birth_date,
                group_name,
                team_short_name,
                group_id,
                competition_team_id,
            ) in enumerate(rows):
                self.table.setItem(row_index, 0, QTableWidgetItem(str(registration_id)))
                self.table.setItem(row_index, 1, QTableWidgetItem(str(participant_id)))
                self.table.setItem(row_index, 2, QTableWidgetItem(full_name))
                self.table.setItem(
                    row_index,
                    3,
                    QTableWidgetItem(self.format_date_for_ui(birth_date))
                )
                self.table.setItem(row_index, 4, QTableWidgetItem(group_name))
                self.table.setItem(row_index, 5, QTableWidgetItem(team_short_name))

            self.table.setColumnHidden(0, True)

        self.table.resizeColumnsToContents()

    def get_selected_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите участника")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def add_participant(self):
        dialog = ParticipantDialog(
            self,
            full_name=self.search_input.text().strip()
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        full_name, birth_date = dialog.get_data()

        if not full_name or not birth_date:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            create_participant(full_name, birth_date)
            self.search_input.clear()
            self.load_participants()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить участника:\n\n{error}"
            )

    def edit_selected_participant(self):
        participant_id = self.get_selected_id()

        if participant_id is None:
            return

        selected_row = self.table.selectionModel().selectedRows()[0].row()
        old_full_name = self.table.item(selected_row, 2).text()

        participants = get_participants()
        old_birth_date = ""

        for current_id, full_name, birth_date in participants:
            if current_id == participant_id:
                old_birth_date = birth_date
                break

        dialog = ParticipantDialog(
            self,
            full_name=old_full_name,
            birth_date=old_birth_date
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        new_full_name, new_birth_date = dialog.get_data()

        if not new_full_name or not new_birth_date:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            update_participant(participant_id, new_full_name, new_birth_date)
            self.load_participants()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить участника:\n\n{error}"
            )

    def delete_selected_participant(self):
        participant_id = self.get_selected_id()

        if participant_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление участника",
            "Удалить участника из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_participant(participant_id)
            self.load_participants()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить участника:\n\n{error}"
            )

    def register_selected_participant(self):
        participant_id = self.get_selected_id()

        if participant_id is None:
            return

        dialog = RegisterParticipantDialog(
            self,
            competition_id=self.app_window.selected_competition_id
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        competition_team_id, group_id = dialog.get_data()

        try:
            registration_id = register_participant(
                participant_id,
                competition_team_id,
                group_id,
            )

            self.show_registered_participant(registration_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось зарегистрировать участника:\n\n{error}"
            )

    def remove_selected_registration(self):
        registration_id = self.get_selected_id()

        if registration_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление из соревнования",
            "Убрать участника из этого соревнования?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            remove_participant_registration(registration_id)
            self.load_participants()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось убрать участника из соревнования:\n\n{error}"
            )

    def show_registered_participant(self, registration_id: int):
        self.show_registered_radio.setChecked(True)
        self.load_participants()

        for row in range(self.table.rowCount()):
            if int(self.table.item(row, 0).text()) == registration_id:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break

    @staticmethod
    def format_date_for_ui(date_from_db: str) -> str:
        date = QDate.fromString(date_from_db, "yyyy-MM-dd")

        if not date.isValid():
            return date_from_db

        return date.toString("dd.MM.yyyy")
