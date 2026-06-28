from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
)

from database import (
    get_summary_rows,
    get_ship_categories,
    get_groups,
    get_teams,
)


class SummaryTab(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Поиск по ФИО участника, названию или модели судна"
        )
        self.search_input.textChanged.connect(self.load_summary)

        self.category_filter_checkbox = QCheckBox("Категория")
        self.category_filter_combo = QComboBox()

        self.group_filter_checkbox = QCheckBox("Группа")
        self.group_filter_combo = QComboBox()

        self.team_filter_checkbox = QCheckBox("Команда")
        self.team_filter_combo = QComboBox()

        self.category_filter_checkbox.toggled.connect(self.load_summary)
        self.category_filter_combo.currentIndexChanged.connect(self.load_summary)

        self.group_filter_checkbox.toggled.connect(self.load_summary)
        self.group_filter_combo.currentIndexChanged.connect(self.load_summary)

        self.team_filter_checkbox.toggled.connect(self.load_summary)
        self.team_filter_combo.currentIndexChanged.connect(self.load_summary)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.category_filter_checkbox)
        filters_layout.addWidget(self.category_filter_combo)
        filters_layout.addWidget(self.group_filter_checkbox)
        filters_layout.addWidget(self.group_filter_combo)
        filters_layout.addWidget(self.team_filter_checkbox)
        filters_layout.addWidget(self.team_filter_combo)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout()
        layout.addLayout(filters_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_filter_values()
        self.load_summary()

    def load_filter_values(self):
        self.category_filter_combo.blockSignals(True)
        self.group_filter_combo.blockSignals(True)
        self.team_filter_combo.blockSignals(True)

        self.category_filter_combo.clear()
        self.group_filter_combo.clear()
        self.team_filter_combo.clear()

        for category_id, name in get_ship_categories():
            self.category_filter_combo.addItem(name, category_id)

        for group_id, name in get_groups():
            self.group_filter_combo.addItem(name, group_id)

        for row in get_teams():
            team_id = row[0]
            short_name = row[1]

            self.team_filter_combo.addItem(short_name, team_id)

        self.category_filter_combo.blockSignals(False)
        self.group_filter_combo.blockSignals(False)
        self.team_filter_combo.blockSignals(False)

    def load_summary(self):
        competition_id = self.app_window.selected_competition_id

        if competition_id is None:
            self.table.setRowCount(0)
            return

        category_id = None
        group_id = None
        team_id = None

        if self.category_filter_checkbox.isChecked():
            category_id = self.category_filter_combo.currentData()

        if self.group_filter_checkbox.isChecked():
            group_id = self.group_filter_combo.currentData()

        if self.team_filter_checkbox.isChecked():
            team_id = self.team_filter_combo.currentData()

        stand_judges, rows = get_summary_rows(
            competition_id=competition_id,
            search=self.search_input.text(),
            category_id=category_id,
            group_id=group_id,
            team_id=team_id,
        )

        headers = [
            "ID",
            "ФИО",
            "Название",
            "Модель",
            "Масштаб",
            "Частота",
            "Категория",
            "Группа",
            "Команда",
        ]

        headers.extend([
            judge_name for _judge_id, judge_name in stand_judges
        ])

        headers.extend([
            "Стенд среднее",
            "1",
            "2",
            "3",
            "Балл за ход",
            "Сумма",
        ])

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row["ship_id"],
                row["participant_full_name"],
                row["ship_name"],
                row["ship_model"],
                row["scale"],
                row["channel"],
                row["category_name"],
                row["group_name"],
                row["team_short_name"],
            ]

            values.extend(row["stand_scores"])

            values.extend([
                row["stand_average"],
                row["attempt_scores"][0],
                row["attempt_scores"][1],
                row["attempt_scores"][2],
                row["movement_score"],
                row["total_score"],
            ])

            for column_index, value in enumerate(values):
                self.table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(self.format_value(value))
                )

        self.table.resizeColumnsToContents()

    @staticmethod
    def format_value(value):
        if value is None:
            return ""

        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")

        return str(value)
