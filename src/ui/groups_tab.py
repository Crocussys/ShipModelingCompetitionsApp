from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QInputDialog,
)

from database import (
    get_groups,
    create_group,
    update_group,
    delete_group,
)


class GroupsTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию группы")
        self.search_input.textChanged.connect(self.load_groups)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Группа"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        self.add_button.clicked.connect(self.add_group)
        self.edit_button.clicked.connect(self.edit_selected_group)
        self.delete_button.clicked.connect(self.delete_selected_group)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.add_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_groups()

    def get_selected_group_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите группу")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def load_groups(self):
        search = self.search_input.text()
        groups = get_groups(search=search)

        self.table.setRowCount(len(groups))

        for row_index, (group_id, name) in enumerate(groups):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(group_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(name))

        self.table.resizeColumnsToContents()

    def add_group(self):
        initial_name = self.search_input.text().strip()

        name, ok = QInputDialog.getText(
            self,
            "Добавление группы",
            "Введите название группы:",
            text=initial_name
        )

        name = name.strip()

        if not ok or not name:
            return

        try:
            create_group(name)
            self.search_input.clear()
            self.load_groups()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить группу:\n\n{error}"
            )

    def edit_selected_group(self):
        group_id = self.get_selected_group_id()

        if group_id is None:
            return

        selected_row = self.table.selectionModel().selectedRows()[0].row()
        old_name = self.table.item(selected_row, 1).text()

        new_name, ok = QInputDialog.getText(
            self,
            "Редактирование группы",
            "Введите новое название группы:",
            text=old_name
        )

        new_name = new_name.strip()

        if not ok or not new_name:
            return

        try:
            update_group(group_id, new_name)
            self.load_groups()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить группу:\n\n{error}"
            )

    def delete_selected_group(self):
        group_id = self.get_selected_group_id()

        if group_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление группы",
            "Удалить группу из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_group(group_id)
            self.load_groups()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить группу:\n\n{error}"
            )
