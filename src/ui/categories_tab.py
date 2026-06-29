from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from database import (
    get_ship_categories,
    create_ship_category,
    update_ship_category,
    delete_ship_category,
)
from ui.category_dialog import CategoryDialog


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

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Категория",
            "Протокол №1",
            "Протокол №2",
            "Протокол №3",
        ])
        self.table.setRowCount(len(categories))

        for row_index, (
            category_id,
            name,
            protocol_1,
            protocol_2,
            protocol_3,
        ) in enumerate(categories):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(category_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(name))
            self.table.setItem(row_index, 2, QTableWidgetItem("Да" if protocol_1 else "Нет"))
            self.table.setItem(row_index, 3, QTableWidgetItem("Да" if protocol_2 else "Нет"))
            self.table.setItem(row_index, 4, QTableWidgetItem("Да" if protocol_3 else "Нет"))

        self.table.resizeColumnsToContents()

    def add_category(self):
        initial_name = self.search_input.text().strip()

        dialog = CategoryDialog(
            self,
            name=initial_name,
            protocol_1=False,
            protocol_2=False,
            protocol_3=False,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        name, protocol_1, protocol_2, protocol_3 = dialog.get_data()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название категории")
            return

        try:
            create_ship_category(
                name,
                protocol_1,
                protocol_2,
                protocol_3,
            )

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
        old_p1 = self.table.item(selected_row, 2).text() == "Да"
        old_p2 = self.table.item(selected_row, 3).text() == "Да"
        old_p3 = self.table.item(selected_row, 4).text() == "Да"

        dialog = CategoryDialog(
            self,
            name=old_name,
            protocol_1=old_p1,
            protocol_2=old_p2,
            protocol_3=old_p3,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        new_name, protocol_1, protocol_2, protocol_3 = dialog.get_data()

        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Введите название категории")
            return

        try:
            update_ship_category(
                category_id,
                new_name,
                protocol_1,
                protocol_2,
                protocol_3,
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
