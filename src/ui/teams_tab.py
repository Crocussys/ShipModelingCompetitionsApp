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
    QInputDialog,
)

from database import (
    get_teams,
    get_teams_for_competition,
    create_team,
    update_team,
    delete_team,
    assign_team_to_competition,
    remove_team_from_competition,
    is_team_assigned,
)

from ui.team_dialog import TeamDialog


class TeamsTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.show_competition_radio = QRadioButton("Команды этого соревнования")
        self.show_all_radio = QRadioButton("Все команды")
        self.show_competition_radio.setChecked(True)

        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.show_competition_radio)
        self.filter_group.addButton(self.show_all_radio)

        self.show_competition_radio.toggled.connect(self.update_mode)
        self.show_all_radio.toggled.connect(self.update_mode)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по короткому названию")
        self.search_input.textChanged.connect(self.load_teams)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.register_button = QPushButton("Зарегистрировать команду")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        self.remove_from_competition_button = QPushButton("Убрать из соревнования")

        self.add_button.clicked.connect(self.add_team)
        self.edit_button.clicked.connect(self.edit_selected_team)
        self.delete_button.clicked.connect(self.delete_selected_team)

        self.register_button.clicked.connect(self.register_team)
        self.remove_from_competition_button.clicked.connect(
            self.remove_selected_team_from_competition
        )

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.show_competition_radio)
        filter_layout.addWidget(self.show_all_radio)
        filter_layout.addStretch()

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)

        self.actions_layout = QHBoxLayout()
        self.actions_layout.addWidget(self.register_button)
        self.actions_layout.addWidget(self.add_button)
        self.actions_layout.addWidget(self.edit_button)
        self.actions_layout.addWidget(self.delete_button)
        self.actions_layout.addWidget(self.remove_from_competition_button)
        self.actions_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(filter_layout)
        layout.addLayout(search_layout)
        layout.addLayout(self.actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.update_mode()

    def update_mode(self):
        competition_mode = self.show_competition_radio.isChecked()

        self.register_button.setVisible(not competition_mode)
        self.add_button.setVisible(not competition_mode)
        self.edit_button.setVisible(not competition_mode)
        self.delete_button.setVisible(not competition_mode)

        self.remove_from_competition_button.setVisible(competition_mode)

        self.load_teams()

    def reset_mode(self):
        self.show_competition_radio.setChecked(True)
        self.update_mode()

    def load_teams(self):
        search = self.search_input.text()
        competition_id = self.app_window.selected_competition_id

        if self.show_competition_radio.isChecked():
            teams = get_teams_for_competition(competition_id, search)

            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Короткое название",
                "Организация",
                "Район",
                "Тренер",
            ])

            self.table.setRowCount(len(teams))

            for row_index, (
                team_id,
                short_name,
                organization,
                district_name,
                coach,
            ) in enumerate(teams):
                self.table.setItem(row_index, 0, QTableWidgetItem(str(team_id)))
                self.table.setItem(row_index, 1, QTableWidgetItem(short_name))
                self.table.setItem(row_index, 2, QTableWidgetItem(organization))
                self.table.setItem(row_index, 3, QTableWidgetItem(district_name))
                self.table.setItem(row_index, 4, QTableWidgetItem(coach))

        else:
            teams = get_teams(search)

            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Участвует",
                "Короткое название",
                "Организация",
                "Район",
            ])

            self.table.setRowCount(len(teams))

            for row_index, (
                team_id,
                short_name,
                organization,
                district_id,
                district_name,
            ) in enumerate(teams):
                assigned = is_team_assigned(team_id, competition_id)

                self.table.setItem(row_index, 0, QTableWidgetItem(str(team_id)))
                self.table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem("Да" if assigned else "Нет")
                )
                self.table.setItem(row_index, 2, QTableWidgetItem(short_name))
                self.table.setItem(row_index, 3, QTableWidgetItem(organization))
                self.table.setItem(row_index, 4, QTableWidgetItem(district_name))

        self.table.resizeColumnsToContents()

    def get_selected_team_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите команду")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def add_team(self):
        dialog = TeamDialog(
            self,
            short_name=self.search_input.text().strip()
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        short_name, organization, district_id = dialog.get_data()

        if not short_name or not organization or district_id is None:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            create_team(short_name, organization, district_id)
            self.search_input.clear()
            self.load_teams()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить команду:\n\n{error}"
            )

    def edit_selected_team(self):
        team_id = self.get_selected_team_id()

        if team_id is None:
            return

        selected_row = self.table.selectionModel().selectedRows()[0].row()

        old_short_name = self.table.item(selected_row, 2).text()
        old_organization = self.table.item(selected_row, 3).text()

        teams = get_teams()

        old_district_id = None

        for current_team_id, short_name, organization, district_id, district_name in teams:
            if current_team_id == team_id:
                old_district_id = district_id
                break

        dialog = TeamDialog(
            self,
            short_name=old_short_name,
            organization=old_organization,
            district_id=old_district_id,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        new_short_name, new_organization, new_district_id = dialog.get_data()

        if not new_short_name or not new_organization or new_district_id is None:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            update_team(
                team_id,
                new_short_name,
                new_organization,
                new_district_id,
            )

            self.load_teams()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить команду:\n\n{error}"
            )

    def delete_selected_team(self):
        team_id = self.get_selected_team_id()

        if team_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление команды",
            "Удалить команду из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_team(team_id)
            self.load_teams()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить команду:\n\n{error}"
            )

    def register_team(self):
        team_id = self.get_selected_team_id()

        if team_id is None:
            return

        coach, ok = QInputDialog.getText(
            self,
            "Регистрация команды",
            "Введите ФИО тренера или тренеров:"
        )

        if not ok:
            return

        try:
            assign_team_to_competition(
                team_id,
                self.app_window.selected_competition_id,
                coach.strip(),
            )

            self.load_teams()
            self.show_competition_team(team_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось зарегистрировать команду:\n\n{error}"
            )

    def remove_selected_team_from_competition(self):
        team_id = self.get_selected_team_id()

        if team_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление из соревнования",
            "Убрать команду из этого соревнования?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            remove_team_from_competition(
                team_id,
                self.app_window.selected_competition_id,
            )

            self.load_teams()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось убрать команду из соревнования:\n\n{error}"
            )

    def show_competition_team(self, team_id: int):
        self.show_competition_radio.setChecked(True)
        self.load_teams()

        for row in range(self.table.rowCount()):
            if int(self.table.item(row, 0).text()) == team_id:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break
