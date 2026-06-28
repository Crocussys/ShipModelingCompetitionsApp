from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QHBoxLayout,
)

from database import (
    get_competitions,
    create_competition,
)


class SelectCompetitionPage(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.select_label = QLabel("Выберите соревнование")
        self.select_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.combo_box = QComboBox()
        self.combo_box.setFixedWidth(350)

        self.next_button = QPushButton("Далее")
        self.next_button.clicked.connect(self.go_next)
        self.next_button.setFixedWidth(150)

        self.separator_label = QLabel("---- или ----")
        self.separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.create_label = QLabel("Создайте новое соревнование")
        self.create_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название соревнования")
        self.name_input.setFixedWidth(350)

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_new_competition)
        self.create_button.setFixedWidth(150)

        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(self.select_label)
        content_layout.addWidget(self.combo_box)
        content_layout.addWidget(
            self.next_button,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        content_layout.addSpacing(20)
        content_layout.addWidget(self.separator_label)
        content_layout.addSpacing(20)

        content_layout.addWidget(self.create_label)
        content_layout.addWidget(self.name_input)
        content_layout.addWidget(
            self.create_button,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setMaximumWidth(450)   # подбери по вкусу

        main_layout = QHBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(content_widget)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.load_competitions()

    def load_competitions(self):
        self.combo_box.clear()

        competitions = get_competitions()

        for competition_id, name in competitions:
            self.combo_box.addItem(name, competition_id)

        has_competitions = len(competitions) > 0

        self.select_label.setVisible(has_competitions)
        self.combo_box.setVisible(has_competitions)
        self.next_button.setVisible(has_competitions)
        self.separator_label.setVisible(has_competitions)

    def go_next(self):
        competition_id = self.combo_box.currentData()

        if competition_id is None:
            return

        self.app_window.selected_competition_id = competition_id
        self.app_window.show_next_page()

    def create_new_competition(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите название соревнования"
            )
            return

        try:
            competition_id = create_competition(name)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать соревнование:\n\n{error}"
            )
            return

        self.app_window.selected_competition_id = competition_id
        self.name_input.clear()
        self.load_competitions()
        self.app_window.show_next_page()
