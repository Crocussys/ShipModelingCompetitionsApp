from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

from database import (
    get_secondary_protocol_header_data,
    get_summary_rows,
)


class SecondaryProtocolDialog(QDialog):
    def __init__(
        self,
        parent=None,
        competition_id=None,
        protocol_number=None,
        category_id=None,
        group_id=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(f"Протокол №{protocol_number}")
        self.resize(1000, 700)

        self.protocol_number = protocol_number

        data = get_secondary_protocol_header_data(
            competition_id,
            category_id,
            group_id,
        )

        layout = QVBoxLayout()

        approve_block = QWidget()
        approve_layout = QVBoxLayout()
        approve_layout.setContentsMargins(0, 0, 0, 0)

        approve_label_1 = QLabel('"УТВЕРЖДАЮ"')
        approve_label_2 = QLabel("Главный судья соревнований")

        approve_label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        approve_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        approve_layout.addWidget(approve_label_1)
        approve_layout.addWidget(approve_label_2)

        approve_block.setLayout(approve_layout)

        approve_row = QHBoxLayout()
        approve_row.addWidget(approve_block)
        approve_row.addStretch()

        layout.addLayout(approve_row)

        title = QLabel("ПРОТОКОЛ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        event_row = QHBoxLayout()

        main_judge_label = QLabel(data["main_judge_short_name"])
        main_judge_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignVCenter
        )

        event_label = QLabel(
            'областного первенства по судомоделированию среди учащихся "PRO-Судо"'
        )
        event_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_spacer_label = QLabel("")

        event_row.addWidget(main_judge_label, 1)
        event_row.addWidget(event_label, 2)
        event_row.addWidget(right_spacer_label, 1)

        layout.addLayout(event_row)

        class_label = QLabel(
            f"в классе моделей {data['category_name']}, "
            f"{data['group_name']} возрастная группа"
        )
        class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(class_label)

        place_label = QLabel("Озеро Свято городский округ Навашинский")
        place_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(place_label)

        layout.addSpacing(20)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table, 1)

        self.load_protocol_table(
            competition_id=competition_id,
            category_id=category_id,
            group_id=group_id,
        )

        secretary_label = QLabel(
            f"Главный секретарь соревнований: {data['secretary_short_name']}"
        )
        secretary_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addSpacing(20)
        layout.addWidget(secretary_label)

        self.print_button = QPushButton("Распечатать")
        self.print_button.setFixedWidth(140)
        self.print_button.clicked.connect(self.print_protocol)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.print_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_protocol_table(
        self,
        competition_id: int,
        category_id: int,
        group_id: int,
    ):
        stand_judges, rows = get_summary_rows(
            competition_id=competition_id,
            category_id=category_id,
            group_id=group_id,
        )

        stand_count = len(stand_judges)

        if self.protocol_number == 1:
            column_count = 8 + stand_count + 1 + 3 + 4
        elif self.protocol_number == 2:
            column_count = 8 + 3 + 3
        else:
            column_count = 6 + 6 + 3

        self.table.setColumnCount(column_count)
        self.table.setRowCount(len(rows) + 2)

        if self.protocol_number == 1:
            self.create_protocol_1_header(stand_count)
        elif self.protocol_number == 2:
            self.create_protocol_2_header()
        else:
            self.create_protocol_3_header()

        for row_index, row in enumerate(rows, start=2):
            values = [
                row_index - 1,
                row["district_name"],
                row["organization"],
                row["coach"],
                self.format_child_name(row["participant_full_name"]),
                row["ship_name"],
                row["channel"],
                0,
            ]

            if self.protocol_number == 1:
                values.extend(row["stand_scores"])

                values.extend([
                    row["stand_average"],
                    row["attempt_scores"][0],
                    row["attempt_scores"][1],
                    row["attempt_scores"][2],
                    row["movement_score"],
                    row["total_score"],
                    row["place"],
                    row["team_score"],
                ])

            elif self.protocol_number == 2:
                values.extend([
                    row["attempt_scores"][0],
                    row["attempt_scores"][1],
                    row["attempt_scores"][2],
                    row["movement_score"],
                    row["place"],
                    row["team_score"],
                ])

            else:
                values = [
                    row_index - 1,
                    row["district_name"],
                    row["organization"],
                    row["coach"],
                    self.format_child_name(row["participant_full_name"]),
                    row["ship_name"],
                    row["laps"][0],
                    row["seconds"][0],
                    row["laps"][1],
                    row["seconds"][1],
                    row["laps"][2],
                    row["seconds"][2],
                    row["total_laps"],
                    row["place"],
                    row["team_score"],
                ]

            for column_index, value in enumerate(values):
                self.table.setItem(
                    row_index,
                    column_index,
                    self.make_center_item(self.format_value(value))
                )

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def create_protocol_1_header(self, stand_count: int):
        headers_left = [
            "№",
            "Район",
            "О.О.",
            "Ф.И.О.\nпедагога",
            "Ф.И.\nребёнка",
            "Название\nмодели",
            "ДОК",
            "Теория",
        ]

        for column, text in enumerate(headers_left):
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

        stand_start = len(headers_left)

        if stand_count > 0:
            self.table.setSpan(0, stand_start, 1, stand_count)
            self.table.setItem(
                0,
                stand_start,
                self.make_center_item("Стендовая оценка")
            )

            for index in range(stand_count):
                self.table.setItem(
                    1,
                    stand_start + index,
                    self.make_center_item(str(index + 1))
                )

        stand_average_column = stand_start + stand_count

        self.table.setSpan(0, stand_average_column, 2, 1)
        self.table.setItem(
            0,
            stand_average_column,
            self.make_center_item("Средний\nбалл стенда")
        )

        attempt_start = stand_average_column + 1

        self.table.setSpan(0, attempt_start, 1, 3)
        self.table.setItem(
            0,
            attempt_start,
            self.make_center_item("Попытка")
        )

        for index in range(3):
            self.table.setItem(
                1,
                attempt_start + index,
                self.make_center_item(str(index + 1))
            )

        tail_headers = [
            "Балл\nза ход",
            "Сумма",
            "Место",
            "Балл\nв команду",
        ]

        tail_start = attempt_start + 3

        for index, text in enumerate(tail_headers):
            column = tail_start + index
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

    def create_protocol_2_header(self):
        headers_left = [
            "№",
            "Район",
            "О.О.",
            "Ф.И.О.\nпедагога",
            "Ф.И.\nребёнка",
            "Название\nмодели",
            "ДОК",
            "Теория",
        ]

        for column, text in enumerate(headers_left):
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

        attempt_start = len(headers_left)

        self.table.setSpan(0, attempt_start, 1, 3)
        self.table.setItem(
            0,
            attempt_start,
            self.make_center_item("Попытка")
        )

        for index in range(3):
            self.table.setItem(
                1,
                attempt_start + index,
                self.make_center_item(str(index + 1))
            )

        tail_headers = [
            "Балл\nза ход",
            "Место",
            "Балл\nв команду",
        ]

        tail_start = attempt_start + 3

        for index, text in enumerate(tail_headers):
            column = tail_start + index
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

    def create_protocol_3_header(self):
        headers_left = [
            "№",
            "Район",
            "О.О.",
            "Ф.И.О.\nпедагога",
            "Ф.И.\nребёнка",
            "Название\nмодели",
        ]

        for column, text in enumerate(headers_left):
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

        attempt_start = len(headers_left)

        for attempt_index in range(3):
            start_column = attempt_start + attempt_index * 2

            self.table.setSpan(0, start_column, 1, 2)
            self.table.setItem(
                0,
                start_column,
                self.make_center_item(f"{attempt_index + 1} заезд")
            )

            self.table.setItem(
                1,
                start_column,
                self.make_center_item("круги")
            )

            self.table.setItem(
                1,
                start_column + 1,
                self.make_center_item("секунды")
            )

        tail_start = attempt_start + 6

        tail_headers = [
            "Сумма\nкругов",
            "Место",
            "Балл\nв команду",
        ]

        for index, text in enumerate(tail_headers):
            column = tail_start + index
            self.table.setSpan(0, column, 2, 1)
            self.table.setItem(0, column, self.make_center_item(text))

    def print_protocol(self):
        QMessageBox.information(
            self,
            "Печать",
            "Это пока не работает"
        )

    @staticmethod
    def make_center_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item


    @staticmethod
    def format_value(value):
        if value is None:
            return ""

        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")

        return str(value)


    @staticmethod
    def format_child_name(full_name: str) -> str:
        parts = full_name.split()

        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"

        return full_name
