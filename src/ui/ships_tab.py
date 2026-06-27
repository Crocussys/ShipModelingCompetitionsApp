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
    get_ships,
    create_ship,
    update_ship,
    delete_ship,
    is_ship_registered,
    get_registered_ships,
    register_ship,
    remove_ship_registration,
    get_ship_categories,
)

from ui.ship_dialog import ShipDialog
from ui.register_ship_dialog import RegisterShipDialog


class ShipsTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.show_registered_radio = QRadioButton("Судна этого соревнования")
        self.show_all_radio = QRadioButton("Все судна")
        self.show_registered_radio.setChecked(True)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.show_registered_radio)
        self.mode_group.addButton(self.show_all_radio)

        self.show_registered_radio.toggled.connect(self.update_mode)
        self.show_all_radio.toggled.connect(self.update_mode)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию, модели или ФИО")
        self.search_input.textChanged.connect(self.load_ships)

        self.category_filter_checkbox = QCheckBox("Категория")
        self.category_filter_combo = QComboBox()

        self.category_filter_checkbox.toggled.connect(self.load_ships)
        self.category_filter_combo.currentIndexChanged.connect(self.load_ships)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.register_button = QPushButton("Зарегистрировать судно")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.remove_button = QPushButton("Убрать из соревнования")

        self.register_button.clicked.connect(self.register_selected_ship)
        self.add_button.clicked.connect(self.add_ship)
        self.edit_button.clicked.connect(self.edit_selected_ship)
        self.delete_button.clicked.connect(self.delete_selected_ship)
        self.remove_button.clicked.connect(self.remove_selected_registration)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.show_registered_radio)
        mode_layout.addWidget(self.show_all_radio)
        mode_layout.addStretch()

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.category_filter_checkbox)
        filters_layout.addWidget(self.category_filter_combo)

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

        self.load_filter_values()
        self.load_ships()

    def load_filter_values(self):
        self.category_filter_combo.blockSignals(True)
        self.category_filter_combo.clear()

        for category_id, name in get_ship_categories():
            self.category_filter_combo.addItem(name, category_id)

        self.category_filter_combo.blockSignals(False)

    def get_selected_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите судно")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def load_ships(self):
        search = self.search_input.text()
        competition_id = self.app_window.selected_competition_id

        category_id = None
        if self.category_filter_checkbox.isChecked():
            category_id = self.category_filter_combo.currentData()

        if self.show_all_radio.isChecked():
            ships = get_ships(search=search, category_id=category_id)

            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "ID",
                "Участвует",
                "Название",
                "Модель",
                "Категория",
                "Масштаб",
            ])

            self.table.setRowCount(len(ships))

            for row_index, (
                ship_id,
                name,
                model,
                category_id,
                category_name,
                scale,
            ) in enumerate(ships):
                registered = is_ship_registered(ship_id, competition_id)

                self.table.setItem(row_index, 0, QTableWidgetItem(str(ship_id)))
                self.table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem("Да" if registered else "Нет")
                )
                self.table.setItem(row_index, 2, QTableWidgetItem(name))
                self.table.setItem(row_index, 3, QTableWidgetItem(model))
                self.table.setItem(row_index, 4, QTableWidgetItem(category_name))
                self.table.setItem(row_index, 5, QTableWidgetItem(scale))

        else:
            rows = get_registered_ships(
                competition_id=competition_id,
                search=search,
                category_id=category_id,
            )

            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels([
                "ID регистрации",
                "ID",
                "ФИО участника",
                "Название",
                "Модель",
                "Категория",
                "Масштаб",
                "Канал/частота",
            ])

            self.table.setRowCount(len(rows))

            for row_index, (
                registration_id,
                ship_id,
                participant_full_name,
                name,
                model,
                category_id,
                category_name,
                scale,
                channel,
            ) in enumerate(rows):
                self.table.setItem(row_index, 0, QTableWidgetItem(str(registration_id)))
                self.table.setItem(row_index, 1, QTableWidgetItem(str(ship_id)))
                self.table.setItem(row_index, 2, QTableWidgetItem(participant_full_name))
                self.table.setItem(row_index, 3, QTableWidgetItem(name))
                self.table.setItem(row_index, 4, QTableWidgetItem(model))
                self.table.setItem(row_index, 5, QTableWidgetItem(category_name))
                self.table.setItem(row_index, 6, QTableWidgetItem(scale))
                self.table.setItem(row_index, 7, QTableWidgetItem(channel))

            self.table.setColumnHidden(0, True)

        self.table.resizeColumnsToContents()

    def add_ship(self):
        dialog = ShipDialog(self)

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        name, model, category_id, scale = dialog.get_data()

        if category_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return

        try:
            create_ship(name, model, category_id, scale)
            self.load_ships()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить судно:\n\n{error}"
            )

    def edit_selected_ship(self):
        ship_id = self.get_selected_id()

        if ship_id is None:
            return

        row = self.table.selectionModel().selectedRows()[0].row()

        old_name = self.table.item(row, 2).text()
        old_model = self.table.item(row, 3).text()
        old_scale = self.table.item(row, 5).text()

        ships = get_ships()
        old_category_id = None

        for current_ship_id, name, model, category_id, category_name, scale in ships:
            if current_ship_id == ship_id:
                old_category_id = category_id
                break

        dialog = ShipDialog(
            self,
            name=old_name,
            model=old_model,
            category_id=old_category_id,
            scale=old_scale,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        new_name, new_model, new_category_id, new_scale = dialog.get_data()

        if new_category_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return

        try:
            update_ship(
                ship_id,
                new_name,
                new_model,
                new_category_id,
                new_scale,
            )
            self.load_ships()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось изменить судно:\n\n{error}"
            )

    def delete_selected_ship(self):
        ship_id = self.get_selected_id()

        if ship_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление судна",
            "Удалить судно из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_ship(ship_id)
            self.load_ships()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить судно:\n\n{error}"
            )

    def register_selected_ship(self):
        ship_id = self.get_selected_id()

        if ship_id is None:
            return

        dialog = RegisterShipDialog(
            self,
            competition_id=self.app_window.selected_competition_id
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        competition_team_participant_id, channel = dialog.get_data()

        try:
            registration_id = register_ship(
                ship_id,
                competition_team_participant_id,
                channel,
            )

            self.show_registered_ship(registration_id)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось зарегистрировать судно:\n\n{error}"
            )

    def remove_selected_registration(self):
        registration_id = self.get_selected_id()

        if registration_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление из соревнования",
            "Убрать судно из этого соревнования?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            remove_ship_registration(registration_id)
            self.load_ships()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось убрать судно из соревнования:\n\n{error}"
            )

    def show_registered_ship(self, registration_id: int):
        self.show_registered_radio.setChecked(True)
        self.load_ships()

        for row in range(self.table.rowCount()):
            if int(self.table.item(row, 0).text()) == registration_id:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 1))
                break
