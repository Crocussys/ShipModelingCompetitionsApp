from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QPushButton,
    QMessageBox,
    QCheckBox,
    QWidget,
)

from database import (
    get_start_protocol,
    get_main_judge_short_name,
    get_start_protocol_ships,
    save_start_result,
    update_start_protocol_status,
    START_PROTOCOL_ACCEPTED,
    get_start_result_values,
    delete_start_result,
)


FORWARD_ROWS = [
    ("Передний ход I", 6),
    ("III", 9),
    ("II", 6),
    ("I", 6),
    ("III", 9),
    ("IV", 6),
    ("IV", 6),
    ("V", 9),
    ("I", 6),
    ("VI", 6),
    ("V", 9),
]

EXTRA_ROWS = [
    ("Задний ход I", 12),
    ("Швартовка", 10),
]


class PenaltySpinBox(QSpinBox):
    def __init__(self, maximum: int, down_step: int, parent=None):
        super().__init__(parent)

        self.down_step = down_step

        self.setRange(0, maximum)
        self.setValue(maximum)

    def stepBy(self, steps: int):
        if steps < 0:
            new_value = self.value() - self.down_step * abs(steps)
        else:
            new_value = self.value() + steps

        self.setValue(new_value)


class StartResultDialog(QDialog):
    def __init__(self, parent=None, protocol_id=None):
        super().__init__(parent)

        self.protocol_id = protocol_id
        self.score_widgets = {}
        self.attempt_checkboxes = {}
        self.column_attempts = {}

        self.setWindowTitle("Стартовый протокол")
        self.resize(1200, 700)

        protocol = get_start_protocol(protocol_id)

        if protocol is None:
            QMessageBox.critical(self, "Ошибка", "Протокол не найден")
            return

        (
            protocol_id,
            judge_full_name,
            category_name,
            group_name,
            competition_id,
        ) = protocol

        main_judge_short_name = get_main_judge_short_name(competition_id)

        layout = QVBoxLayout()

        title = QLabel(
            'ПРОТОКОЛ областного первенства по судомоделированию '
            'среди учащихся "PRO-Судо"'
        )
        title.setAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(title)

        header_layout = QHBoxLayout()

        left_label = QLabel(
            f"Модель класса {category_name} возрастная группа {group_name}"
        )

        right_label = QLabel(
            f"Главный судья: {main_judge_short_name}"
        )

        header_layout.addWidget(left_label)
        header_layout.addStretch()
        header_layout.addWidget(right_label)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.table)

        self.save_button = QPushButton("Сохранить")
        self.save_button.setFixedWidth(140)
        self.save_button.clicked.connect(self.save)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_table()

    def load_table(self):
        ships = get_start_protocol_ships(self.protocol_id)

        attempts_per_ship = 3
        fixed_columns = 1
        column_count = fixed_columns + len(ships) * attempts_per_ship

        self.table.setColumnCount(column_count)
        self.table.setRowCount(20)

        self.table.setSpan(0, 0, 1, 1)
        self.table.setItem(0, 0, QTableWidgetItem("НОМЕР, КОМАНДА"))
        self.table.setItem(1, 0, QTableWidgetItem("ФАМИЛИЯ, ИМЯ"))
        self.table.setItem(2, 0, QTableWidgetItem("МОДЕЛЬ,\nМАСШТАБ"))
        self.table.setItem(3, 0, QTableWidgetItem("КАНАЛ,\nЧАСТОТА"))
        self.table.setItem(4, 0, QTableWidgetItem(""))

        row_index = 5

        for label, _maximum in FORWARD_ROWS:
            self.table.setItem(row_index, 0, QTableWidgetItem(label))
            row_index += 1

        for label, _maximum in EXTRA_ROWS:
            self.table.setItem(row_index, 0, QTableWidgetItem(label))
            row_index += 1

        self.table.setItem(row_index, 0, QTableWidgetItem("Итого"))
        row_index += 1

        self.table.setItem(row_index, 0, QTableWidgetItem("Средняя оценка за ход"))

        for ship_index, (
            registered_ship_id,
            participant_full_name,
            team_id,
            organization,
            model,
            scale,
            channel,
        ) in enumerate(ships):
            start_column = fixed_columns + ship_index * attempts_per_ship

            self.table.setSpan(0, start_column, 1, attempts_per_ship)
            self.table.setSpan(1, start_column, 1, attempts_per_ship)
            self.table.setSpan(2, start_column, 1, attempts_per_ship)
            self.table.setSpan(3, start_column, 1, attempts_per_ship)

            self.table.setItem(
                0,
                start_column,
                QTableWidgetItem(f"{team_id}, {organization}")
            )
            self.table.setItem(
                1,
                start_column,
                QTableWidgetItem(self.format_participant_name(participant_full_name))
            )
            self.table.setItem(
                2,
                start_column,
                QTableWidgetItem(f"{model}\n{scale}")
            )
            self.table.setItem(
                3,
                start_column,
                QTableWidgetItem(channel)
            )

            for attempt in range(1, 4):
                column = start_column + attempt - 1

                checkbox = QCheckBox(str(attempt))
                checkbox.setChecked(True)
                checkbox.toggled.connect(
                    lambda _checked, c=column: self.update_totals(c)
                )

                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout()
                checkbox_layout.addStretch()
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.addStretch()
                checkbox_layout.setContentsMargins(0, 0, 0, 0)

                checkbox_widget.setLayout(checkbox_layout)

                self.table.setCellWidget(4, column, checkbox_widget)

                self.attempt_checkboxes[(registered_ship_id, attempt)] = checkbox
                self.column_attempts[column] = (registered_ship_id, attempt)

                self.create_score_column(
                    registered_ship_id=registered_ship_id,
                    attempt=attempt,
                    column=column,
                )
        
        for column in range(1, column_count):
            self.update_totals(column)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def create_score_column(self, registered_ship_id: int, attempt: int, column: int):
        self.score_widgets[(registered_ship_id, attempt)] = []

        all_rows = FORWARD_ROWS + EXTRA_ROWS
        saved_values = get_start_result_values(
            self.protocol_id,
            registered_ship_id,
            attempt,
        )

        for score_index, (_label, maximum) in enumerate(all_rows):
            row = 5 + score_index

            spin_box = PenaltySpinBox(
                maximum=maximum,
                down_step=get_down_step(maximum),
            )

            if saved_values is not None:
                spin_box.setValue(saved_values[score_index])
            else:
                spin_box.setValue(maximum)

            spin_box.valueChanged.connect(
                lambda _value, c=column: self.update_totals(c)
            )

            self.table.setCellWidget(row, column, spin_box)
            self.score_widgets[(registered_ship_id, attempt)].append(spin_box)

        total_item = QTableWidgetItem("0")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(18, column, total_item)

        average_item = QTableWidgetItem("")
        average_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(19, column, average_item)

    def update_totals(self, column: int):
        total = 0

        for row in range(5, 18):
            widget = self.table.cellWidget(row, column)

            if widget is not None:
                total += widget.value()

        total_item = self.table.item(18, column)

        if total_item is None:
            total_item = QTableWidgetItem()
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(18, column, total_item)

        total_item.setText(str(total))

        ship_start_column = 1 + ((column - 1) // 3) * 3

        checked_totals = []

        for current_column in range(ship_start_column, ship_start_column + 3):
            registered_ship_id, attempt = self.column_attempts[current_column]
            checkbox = self.attempt_checkboxes[(registered_ship_id, attempt)]

            if not checkbox.isChecked():
                continue

            item = self.table.item(18, current_column)

            if item is not None and item.text():
                checked_totals.append(int(item.text()))

        average_text = ""

        if checked_totals:
            average = sum(checked_totals) / len(checked_totals)
            average_text = f"{average:.2f}".rstrip("0").rstrip(".")

        self.table.setSpan(19, ship_start_column, 1, 3)

        average_item = self.table.item(19, ship_start_column)

        if average_item is None:
            average_item = QTableWidgetItem()
            average_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(19, ship_start_column, average_item)

        average_item.setText(average_text)

    def save(self):
        try:
            for (registered_ship_id, attempt), widgets in self.score_widgets.items():
                checkbox = self.attempt_checkboxes[(registered_ship_id, attempt)]

                if not checkbox.isChecked():
                    delete_start_result(
                        self.protocol_id,
                        registered_ship_id,
                        attempt,
                    )
                    continue

                values = [widget.value() for widget in widgets]

                save_start_result(
                    self.protocol_id,
                    registered_ship_id,
                    attempt,
                    *values,
                )

            update_start_protocol_status(
                self.protocol_id,
                START_PROTOCOL_ACCEPTED,
            )

            self.accept()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить результаты:\n\n{error}"
            )

    @staticmethod
    def format_participant_name(full_name: str) -> str:
        parts = full_name.split()

        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"

        return full_name
    

def get_down_step(maximum: int) -> int:
    if maximum == 6:
        return 2

    if maximum == 9:
        return 3

    if maximum == 12:
        return 4

    return 1
