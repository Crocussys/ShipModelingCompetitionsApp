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
    get_team_protocol_rows,
)


class TeamProtocolDialog(QDialog):
    def __init__(self, parent=None, competition_id=None, group_id=None):
        super().__init__(parent)

        self.setWindowTitle("Командный протокол")
        self.resize(1000, 700)

        data = get_secondary_protocol_header_data(
            competition_id=competition_id,
            category_id=None,
            group_id=group_id,
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

        layout.addWidget(approve_block, alignment=Qt.AlignmentFlag.AlignLeft)

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
            f"Командное первенство, {data['group_name']} возрастная группа"
        )
        class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(class_label)

        place_label = QLabel("Озеро Свято городский округ Навашинский")
        place_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(place_label)

        layout.addSpacing(20)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table, 1)

        self.load_table(competition_id, group_id)

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

    def load_table(self, competition_id: int, group_id: int):
        categories, rows = get_team_protocol_rows(
            competition_id=competition_id,
            group_id=group_id,
        )

        headers = [
            "№",
            "Район",
            "О.О.",
            "Ф.И.О.\nпедагога",
        ]

        headers.extend(categories)

        headers.extend([
            "Сумма",
            "Место",
        ])

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row_index + 1,
                row["district_name"],
                row["organization"],
                row["coach"],
            ]

            for category_name in categories:
                values.append(
                    row["category_scores"].get(category_name, "")
                )

            values.extend([
                row["total_score"],
                row["place"],
            ])

            for column_index, value in enumerate(values):
                self.table.setItem(
                    row_index,
                    column_index,
                    self.make_center_item(self.format_value(value))
                )

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

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
