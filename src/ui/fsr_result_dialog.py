from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from database import (
    get_fsr_protocol,
    get_fsr_results,
    save_fsr_result,
    update_fsr_protocol_status,
    FSR_PROTOCOL_ACCEPTED,
)


class FsrResultDialog(QDialog):
    def __init__(self, parent=None, protocol_id=None):
        super().__init__(parent)

        self.protocol_id = protocol_id
        self.inputs = {}

        self.setWindowTitle("FSR")
        self.resize(450, 300)

        protocol = get_fsr_protocol(protocol_id)

        if protocol is None:
            QMessageBox.critical(self, "Ошибка", "Протокол не найден")
            return

        _id, full_name, ship_name, ship_model, category_name, group_name = protocol

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Участник: {full_name}"))
        layout.addWidget(QLabel(f"Судно: {ship_name}"))
        layout.addWidget(QLabel(f"Модель: {ship_model}"))
        layout.addWidget(QLabel(f"Категория: {category_name}"))
        layout.addWidget(QLabel(f"Группа: {group_name}"))

        form_layout = QFormLayout()

        saved = {
            attempt: (laps, seconds)
            for attempt, laps, seconds in get_fsr_results(protocol_id)
        }

        for attempt in (1, 2, 3):
            laps_input = QSpinBox()
            laps_input.setRange(0, 999999)

            seconds_input = QSpinBox()
            seconds_input.setRange(0, 999999)

            if attempt in saved:
                laps, seconds = saved[attempt]
                laps_input.setValue(laps)
                seconds_input.setValue(seconds)

            attempt_layout = QHBoxLayout()
            attempt_layout.addWidget(QLabel("Круги:"))
            attempt_layout.addWidget(laps_input)
            attempt_layout.addWidget(QLabel("Секунды:"))
            attempt_layout.addWidget(seconds_input)

            form_layout.addRow(f"Заезд {attempt}:", attempt_layout)

            self.inputs[attempt] = (laps_input, seconds_input)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Сохранить")
        self.save_button.setFixedWidth(140)
        self.save_button.clicked.connect(self.save)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save(self):
        try:
            for attempt, (laps_input, seconds_input) in self.inputs.items():
                save_fsr_result(
                    self.protocol_id,
                    attempt,
                    laps_input.value(),
                    seconds_input.value(),
                )

            update_fsr_protocol_status(
                self.protocol_id,
                FSR_PROTOCOL_ACCEPTED,
            )

            self.accept()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить FSR:\n\n{error}"
            )
