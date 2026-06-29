from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
)

from database import (
    get_groups,
    get_team_protocol_groups,
)

from ui.team_protocol_dialog import TeamProtocolDialog


class TeamProtocolTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.group_filter_checkbox = QCheckBox("Группа")
        self.group_filter_combo = QComboBox()

        self.group_filter_checkbox.toggled.connect(self.load_protocols)
        self.group_filter_combo.currentIndexChanged.connect(self.load_protocols)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.group_filter_checkbox)
        filters_layout.addWidget(self.group_filter_combo)
        filters_layout.addStretch()

        self.print_button = QPushButton("Распечатать")
        self.print_button.clicked.connect(self.print_protocol)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.print_button)
        actions_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Группа"])
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
        self.group_filter_combo.blockSignals(True)

        self.group_filter_combo.clear()

        for group_id, name in get_groups():
            self.group_filter_combo.addItem(name, group_id)

        self.group_filter_combo.blockSignals(False)

    def load_protocols(self):
        competition_id = self.app_window.selected_competition_id

        if competition_id is None:
            self.table.setRowCount(0)
            return

        group_id = None

        if self.group_filter_checkbox.isChecked():
            group_id = self.group_filter_combo.currentData()

        rows = get_team_protocol_groups(
            competition_id=competition_id,
            group_id=group_id,
        )

        self.table.setRowCount(len(rows))

        for row_index, (group_id, group_name) in enumerate(rows):
            item = QTableWidgetItem(group_name)
            item.setData(1000, group_id)

            self.table.setItem(row_index, 0, item)

        self.table.resizeColumnsToContents()

    def get_selected_group_id(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите протокол")
            return None

        row = selected_rows[0].row()
        return self.table.item(row, 0).data(1000)

    def print_protocol(self):
        QMessageBox.information(
            self,
            "Печать",
            "Это пока не работает"
        )

    def open_selected_protocol(self):
        group_id = self.get_selected_group_id()

        if group_id is None:
            return

        dialog = TeamProtocolDialog(
            self,
            competition_id=self.app_window.selected_competition_id,
            group_id=group_id,
        )

        dialog.exec()
