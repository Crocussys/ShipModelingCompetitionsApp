from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget

from ui.select_competition_page import SelectCompetitionPage
from ui.competition_page import CompetitionPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_competition_id = None

        self.setWindowTitle("Ship modeling competitions")
        self.resize(500, 300)

        self.stack = QStackedWidget()

        self.select_page = SelectCompetitionPage(self)
        self.next_page = CompetitionPage(self)

        self.stack.addWidget(self.select_page)
        self.stack.addWidget(self.next_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def show_select_page(self):
        self.select_page.load_competitions()
        self.stack.setCurrentWidget(self.select_page)

    def show_next_page(self):
        self.next_page.update_page()
        self.stack.setCurrentWidget(self.next_page)
