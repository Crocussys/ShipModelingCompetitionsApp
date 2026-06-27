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
    QDialog,
    QInputDialog,
)

from database import (
    get_judges,
    create_judge,
    update_judge,
    delete_judge,
    assign_judge_to_competition,
    remove_judge_from_competition,
    is_judge_assigned,
    JUDGE_ROLES,
    get_judge_role_name,
)
from database.utils import make_short_name

from ui.judge_dialog import JudgeDialog


class JudgesTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.show_assigned_radio = QRadioButton("Судьи этого соревнования")
        self.show_all_radio = QRadioButton("Все судьи")
        self.show_assigned_radio.setChecked(True)

        self.filter_group = QButtonGroup()
        self.filter_group.addButton(self.show_assigned_radio)
        self.filter_group.addButton(self.show_all_radio)

        self.show_assigned_radio.toggled.connect(self.update_mode)
        self.show_all_radio.toggled.connect(self.update_mode)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО")
        self.search_input.textChanged.connect(self.load_judges)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Кратко", "Участвует"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.assign_button = QPushButton("Участвует")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        self.remove_button = QPushButton("Убрать из соревнования")

        self.add_button.clicked.connect(self.add_judge)
        self.assign_button.clicked.connect(self.assign_selected_judge)
        self.remove_button.clicked.connect(self.remove_selected_judge)
        self.edit_button.clicked.connect(self.edit_selected_judge)
        self.delete_button.clicked.connect(self.delete_selected_judge)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.show_assigned_radio)
        filter_layout.addWidget(self.show_all_radio)
        filter_layout.addStretch()

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.assign_button)
        actions_layout.addWidget(self.add_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addWidget(self.remove_button)
        actions_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(filter_layout)
        layout.addLayout(search_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.update_mode()

    def update_mode(self):
        competition_mode = self.show_assigned_radio.isChecked()

        self.assign_button.setVisible(not competition_mode)
        self.add_button.setVisible(not competition_mode)
        self.edit_button.setVisible(not competition_mode)
        self.delete_button.setVisible(not competition_mode)

        self.remove_button.setVisible(competition_mode)

        self.load_judges()

    def reset_mode(self):
        self.show_assigned_radio.setChecked(True)
        self.update_mode()

    def get_selected_judge_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите судью")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def load_judges(self):
        competition_id = self.app_window.selected_competition_id
        search = self.search_input.text()

        if self.show_all_radio.isChecked():
            judges = get_judges(
                competition_id=None,
                search=search
            )

            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Участвует",
                "ФИО",
                "Кратко",
            ])

            self.table.setRowCount(len(judges))

            for row_index, (judge_id, full_name, short_name) in enumerate(judges):
                assigned = is_judge_assigned(
                    judge_id,
                    competition_id
                )

                self.table.setItem(row_index, 0, QTableWidgetItem(str(judge_id)))
                self.table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem("Да" if assigned else "Нет")
                )
                self.table.setItem(row_index, 2, QTableWidgetItem(full_name))
                self.table.setItem(row_index, 3, QTableWidgetItem(short_name))

        else:
            judges = get_judges(
                competition_id=competition_id,
                search=search
            )

            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "ФИО",
                "Кратко",
                "Роль",
            ])

            self.table.setRowCount(len(judges))

            for row_index, (judge_id, full_name, short_name, role) in enumerate(judges):
                self.table.setItem(row_index, 0, QTableWidgetItem(str(judge_id)))
                self.table.setItem(row_index, 1, QTableWidgetItem(full_name))
                self.table.setItem(row_index, 2, QTableWidgetItem(short_name))
                self.table.setItem(row_index, 3, QTableWidgetItem(get_judge_role_name(role)))

        self.table.resizeColumnsToContents()

    def add_judge(self):
        initial_name = self.search_input.text().strip()
        initial_short_name = make_short_name(initial_name)

        dialog = JudgeDialog(
            self,
            full_name=initial_name,
            short_name=initial_short_name
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        full_name, short_name = dialog.get_data()

        if not full_name or not short_name:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля")
            return

        try:
            judge_id = create_judge(
                full_name,
                short_name
            )

            role_id = self.select_judge_role()

            if role_id is None:
                return

            assign_judge_to_competition(
                judge_id,
                self.app_window.selected_competition_id,
                role_id
            )

            self.show_competition_judge(judge_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить судью:\n\n{error}"
            )

    def assign_selected_judge(self):
        judge_id = self.get_selected_judge_id()

        if judge_id is None:
            return

        role_id = self.select_judge_role()

        if role_id is None:
            return

        assign_judge_to_competition(
            judge_id,
            self.app_window.selected_competition_id,
            role_id
        )

        self.show_competition_judge(judge_id)

    def remove_selected_judge(self):
        judge_id = self.get_selected_judge_id()

        if judge_id is None:
            return

        remove_judge_from_competition(
            judge_id,
            self.app_window.selected_competition_id
        )

        self.load_judges()

    def edit_selected_judge(self):
        judge_id = self.get_selected_judge_id()

        if judge_id is None:
            return

        selected_row = self.table.selectionModel().selectedRows()[0].row()

        old_full_name = self.table.item(selected_row, 2).text()
        old_short_name = self.table.item(selected_row, 3).text()

        dialog = JudgeDialog(
            self,
            full_name=old_full_name,
            short_name=old_short_name
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_full_name, new_short_name = dialog.get_data()

        if not new_full_name or not new_short_name:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля")
            return

        try:
            update_judge(
                judge_id,
                new_full_name,
                new_short_name
            )

            self.load_judges()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить судью:\n\n{error}"
            )

    def delete_selected_judge(self):
        judge_id = self.get_selected_judge_id()

        if judge_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление судьи",
            "Удалить судью полностью из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        delete_judge(judge_id)
        self.load_judges()

    def show_competition_judge(self, judge_id: int):
        self.show_assigned_radio.setChecked(True)
        self.load_judges()

        for row in range(self.table.rowCount()):
            if int(self.table.item(row, 0).text()) == judge_id:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break
    
    def select_judge_role(self) -> int | None:
        role_names = list(JUDGE_ROLES.values())

        selected_role_name, ok = QInputDialog.getItem(
            self,
            "Роль судьи",
            "Выберите роль судьи:",
            role_names,
            role_names.index("Судья"),
            False
        )

        if not ok:
            return None

        for role_id, role_name in JUDGE_ROLES.items():
            if role_name == selected_role_name:
                return role_id

        return None
