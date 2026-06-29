from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QMessageBox,
)

from database import (
    get_stand_protocols,
    get_stand_protocol_status_name,
    update_stand_protocol_status,
    STAND_PROTOCOL_GIVEN,
    get_protocol_1_categories,
    get_groups,
)

from ui.stand_result_dialog import StandResultDialog


class StandTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО судьи или участника")
        self.search_input.textChanged.connect(self.load_stand_protocols)

        self.category_filter_checkbox = QCheckBox("Категория")
        self.category_filter_combo = QComboBox()

        self.group_filter_checkbox = QCheckBox("Группа")
        self.group_filter_combo = QComboBox()

        self.category_filter_checkbox.toggled.connect(self.load_stand_protocols)
        self.category_filter_combo.currentIndexChanged.connect(self.load_stand_protocols)
        self.group_filter_checkbox.toggled.connect(self.load_stand_protocols)
        self.group_filter_combo.currentIndexChanged.connect(self.load_stand_protocols)

        self.print_button = QPushButton("Распечатать")
        self.given_button = QPushButton("Отдан")
        self.fill_button = QPushButton("Заполнить")

        self.print_button.clicked.connect(self.print_protocol)
        self.given_button.clicked.connect(self.mark_as_given)
        self.fill_button.clicked.connect(self.fill_protocol)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.category_filter_checkbox)
        filters_layout.addWidget(self.category_filter_combo)
        filters_layout.addWidget(self.group_filter_checkbox)
        filters_layout.addWidget(self.group_filter_combo)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.print_button)
        actions_layout.addWidget(self.given_button)
        actions_layout.addWidget(self.fill_button)
        actions_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Судья",
            "Категория",
            "Группа",
            "Статус",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(
            lambda _: self.fill_protocol()
        )

        layout = QVBoxLayout()
        layout.addLayout(filters_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_filter_values()
        self.load_stand_protocols()

    def load_filter_values(self):
        self.category_filter_combo.blockSignals(True)
        self.group_filter_combo.blockSignals(True)

        self.category_filter_combo.clear()
        self.group_filter_combo.clear()

        for category_id, name in get_protocol_1_categories():
            self.category_filter_combo.addItem(name, category_id)

        for group_id, name in get_groups():
            self.group_filter_combo.addItem(name, group_id)

        self.category_filter_combo.blockSignals(False)
        self.group_filter_combo.blockSignals(False)

    def load_stand_protocols(self):
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

        protocols = get_stand_protocols(
            competition_id=competition_id,
            search=self.search_input.text(),
            category_id=category_id,
            group_id=group_id,
        )

        self.table.setRowCount(len(protocols))

        for row_index, (
            protocol_id,
            judge_full_name,
            category_name,
            group_name,
            status,
            category_id,
            group_id,
        ) in enumerate(protocols):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(protocol_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(judge_full_name))
            self.table.setItem(row_index, 2, QTableWidgetItem(category_name))
            self.table.setItem(row_index, 3, QTableWidgetItem(group_name))
            self.table.setItem(
                row_index,
                4,
                QTableWidgetItem(get_stand_protocol_status_name(status))
            )

        self.table.resizeColumnsToContents()

    def get_selected_protocol_id(self) -> int | None:
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите протокол")
            return None

        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def print_protocol(self):
        pass

    def mark_as_given(self):
        protocol_id = self.get_selected_protocol_id()

        if protocol_id is None:
            return

        update_stand_protocol_status(
            protocol_id,
            STAND_PROTOCOL_GIVEN
        )

        self.load_stand_protocols()

    def fill_protocol(self):
        protocol_id = self.get_selected_protocol_id()

        if protocol_id is None:
            return

        dialog = StandResultDialog(
            self,
            protocol_id=protocol_id
        )

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.load_stand_protocols()
