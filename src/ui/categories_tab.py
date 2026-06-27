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
    get_ship_categories,
    create_ship_category,
    update_ship_category,
    delete_ship_category,
)


class CategoriesTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию категории")
        self.search_input.textChanged.connect(self.load_categories)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Категория"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        self.add_button.clicked.connect(self.add_category)
        self.edit_button.clicked.connect(self.edit_selected_category)
        self.delete_button.clicked.connect(self.delete_selected_category)

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

        self.load_categories()

    def get_selected_category_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def load_categories(self):
        search = self.search_input.text()
        categories = get_ship_categories(search=search)

        self.table.setRowCount(len(categories))

        for row_index, (category_id, name) in enumerate(categories):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(category_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(name))

        self.table.resizeColumnsToContents()

    def add_category(self):
        initial_name = self.search_input.text().strip()

        name, ok = QInputDialog.getText(
            self,
            "Добавление категории",
            "Введите название категории:",
            text=initial_name
        )

        name = name.strip()

        if not ok or not name:
            return

        try:
            create_ship_category(name)
            self.search_input.clear()
            self.load_categories()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить категорию:\n\n{error}"
            )

    def edit_selected_category(self):
        category_id = self.get_selected_category_id()

        if category_id is None:
            return

        selected_row = self.table.selectionModel().selectedRows()[0].row()
        old_name = self.table.item(selected_row, 1).text()

        new_name, ok = QInputDialog.getText(
            self,
            "Редактирование категории",
            "Введите новое название категории:",
            text=old_name
        )

        new_name = new_name.strip()

        if not ok or not new_name:
            return

        try:
            update_ship_category(
                category_id,
                new_name
            )

            self.load_categories()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить категорию:\n\n{error}"
            )

    def delete_selected_category(self):
        category_id = self.get_selected_category_id()

        if category_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление категории",
            "Удалить категорию из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_ship_category(category_id)
            self.load_categories()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить категорию:\n\n{error}"
            )
