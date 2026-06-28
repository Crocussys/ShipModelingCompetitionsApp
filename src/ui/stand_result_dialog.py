from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QFormLayout,
)

from database import (
    get_stand_protocol,
    get_main_stand_judge_full_name,
    get_stand_protocol_ships,
    save_stand_result,
    update_stand_protocol_status,
    STAND_PROTOCOL_ACCEPTED,
)


class StandResultDialog(QDialog):
    def __init__(self, parent=None, protocol_id=None):
        super().__init__(parent)

        self.protocol_id = protocol_id
        self.score_widgets = {}

        self.setWindowTitle("Карточка индивидуальной стендовой оценки")
        self.resize(900, 600)

        protocol = get_stand_protocol(protocol_id)

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

        main_judge_name = get_main_stand_judge_full_name(competition_id)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Карточка индивидуальной стендовой оценки"))
        
        info_layout = QFormLayout()

        info_layout.addRow(
            "Главный судья:",
            QLabel(main_judge_name)
        )

        info_layout.addRow(
            "Судья:",
            QLabel(judge_full_name)
        )

        layout.addLayout(info_layout)

        layout.addSpacing(20)

        layout.addWidget(QLabel(f"Класс модели {category_name} {group_name}"))

        layout.addSpacing(20)

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.table)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)
        self.save_button.setFixedWidth(140)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_ships()

    def load_ships(self):
        rows = get_stand_protocol_ships(self.protocol_id)

        self.table.setColumnCount(8)
        self.table.setRowCount(len(rows) + 2)

        self.table.setSpan(0, 0, 2, 1)
        self.table.setSpan(0, 1, 2, 1)
        self.table.setSpan(0, 2, 2, 1)
        self.table.setSpan(0, 3, 1, 4)
        self.table.setSpan(0, 7, 2, 1)

        self.table.setItem(0, 0, self.make_center_item("ФИО"))
        self.table.setItem(0, 1, self.make_center_item("№"))
        self.table.setItem(0, 2, self.make_center_item("Масштаб"))
        self.table.setItem(0, 3, self.make_center_item("Оценки по разделам"))
        self.table.setItem(0, 7, self.make_center_item("Итого"))

        self.table.setItem(1, 3, self.make_center_item("Исполнение\n50"))
        self.table.setItem(1, 4, self.make_center_item("Впечатление\n10"))
        self.table.setItem(1, 5, self.make_center_item("Объём работы\n20"))
        self.table.setItem(1, 6, self.make_center_item("Соответствие\n20"))

        self.score_widgets = {}

        maximums = [50, 10, 20, 20]

        for row_index, (
            registered_ship_id,
            participant_full_name,
            team_id,
            scale,
            execution_score,
            impression_score,
            work_volume_score,
            compliance_score,
        ) in enumerate(rows, start=2):
            self.table.setItem(row_index, 0, QTableWidgetItem(participant_full_name))
            self.table.setItem(row_index, 1, self.make_center_item(str(team_id)))
            self.table.setItem(row_index, 2, self.make_center_item(scale))

            total_item = self.make_center_item("0")
            self.table.setItem(row_index, 7, total_item)

            scores = [
                execution_score,
                impression_score,
                work_volume_score,
                compliance_score,
            ]

            widgets = []

            for column_index, (score, maximum) in enumerate(
                zip(scores, maximums),
                start=3,
            ):
                spin_box = QSpinBox()
                spin_box.setRange(0, maximum)

                if score is not None:
                    spin_box.setValue(score)
                else:
                    spin_box.setValue(maximum)

                spin_box.valueChanged.connect(
                    lambda _value, row=row_index: self.update_total(row)
                )

                self.table.setCellWidget(row_index, column_index, spin_box)
                widgets.append(spin_box)

            self.score_widgets[registered_ship_id] = widgets
            self.update_total(row_index)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    @staticmethod
    def make_center_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def save(self):
        try:
            for registered_ship_id, widgets in self.score_widgets.items():
                save_stand_result(
                    self.protocol_id,
                    registered_ship_id,
                    widgets[0].value(),
                    widgets[1].value(),
                    widgets[2].value(),
                    widgets[3].value(),
                )

            update_stand_protocol_status(
                self.protocol_id,
                STAND_PROTOCOL_ACCEPTED
            )

            self.accept()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить результаты:\n\n{error}"
            )

    def update_total(self, row: int):
        total = 0

        for column in range(3, 7):
            widget = self.table.cellWidget(row, column)

            if widget is not None:
                total += widget.value()

        self.table.item(row, 7).setText(str(total))
