from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox,
    QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
)

from database import (
    get_secondary_protocol_rows,
    get_protocol_1_categories,
    get_protocol_1_or_2_categories,
    get_protocol_3_categories,
    get_groups,
)
from ui.secondary_protocol_dialog import SecondaryProtocolDialog


class SecondaryProtocolTab(QWidget):
    def __init__(self, app_window, protocol_number: int):
        super().__init__()

        self.app_window = app_window
        self.protocol_number = protocol_number

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО участника")
        self.search_input.textChanged.connect(self.load_protocols)

        self.category_filter_checkbox = QCheckBox("Категория")
        self.category_filter_combo = QComboBox()

        self.group_filter_checkbox = QCheckBox("Группа")
        self.group_filter_combo = QComboBox()

        self.category_filter_checkbox.toggled.connect(self.load_protocols)
        self.category_filter_combo.currentIndexChanged.connect(self.load_protocols)
        self.group_filter_checkbox.toggled.connect(self.load_protocols)
        self.group_filter_combo.currentIndexChanged.connect(self.load_protocols)

        self.print_button = QPushButton("Распечатать")
        self.print_button.clicked.connect(self.print_protocol)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.category_filter_checkbox)
        filters_layout.addWidget(self.category_filter_combo)
        filters_layout.addWidget(self.group_filter_checkbox)
        filters_layout.addWidget(self.group_filter_combo)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.print_button)
        actions_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Категория", "Группа"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(lambda _: self.open_selected_protocol())

        layout = QVBoxLayout()
        layout.addLayout(filters_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_filter_values()
        self.load_protocols()

    def load_filter_values(self):
        self.category_filter_combo.blockSignals(True)
        self.group_filter_combo.blockSignals(True)

        self.category_filter_combo.clear()
        self.group_filter_combo.clear()

        if self.protocol_number == 1:
            categories = get_protocol_1_categories()
        elif self.protocol_number == 2:
            categories = get_protocol_1_or_2_categories()
        else:
            categories = get_protocol_3_categories()

        for category_id, name in categories:
            self.category_filter_combo.addItem(name, category_id)

        for group_id, name in get_groups():
            self.group_filter_combo.addItem(name, group_id)

        self.category_filter_combo.blockSignals(False)
        self.group_filter_combo.blockSignals(False)

    def load_protocols(self):
        competition_id = self.app_window.selected_competition_id

        if competition_id is None:
            self.table.setRowCount(0)
            return

        category_id = None
        group_id = None

        if self.category_filter_checkbox.isChecked():
            category_id = self.category_filter_combo.currentData()

        if self.group_filter_checkbox.isChecked():
            group_id = self.group_filter_combo.currentData()

        rows = get_secondary_protocol_rows(
            competition_id=competition_id,
            protocol_number=self.protocol_number,
            search=self.search_input.text(),
            category_id=category_id,
            group_id=group_id,
        )

        self.table.setRowCount(len(rows))

        for row_index, (category_id, category_name, group_id, group_name) in enumerate(rows):
            category_item = QTableWidgetItem(category_name)
            category_item.setData(1000, category_id)

            group_item = QTableWidgetItem(group_name)
            group_item.setData(1000, group_id)

            self.table.setItem(row_index, 0, category_item)
            self.table.setItem(row_index, 1, group_item)

        self.table.resizeColumnsToContents()

    def get_selected_pair(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите протокол")
            return None

        row = selected_rows[0].row()

        return (
            self.table.item(row, 0).data(1000),
            self.table.item(row, 1).data(1000),
        )

    def print_protocol(self):
        QMessageBox.information(self, "Печать", "Это пока не работает")

    def open_selected_protocol(self):
        pair = self.get_selected_pair()

        if pair is None:
            return

        category_id, group_id = pair

        dialog = SecondaryProtocolDialog(
            self,
            competition_id=self.app_window.selected_competition_id,
            protocol_number=self.protocol_number,
            category_id=category_id,
            group_id=group_id,
        )

        dialog.exec()
