from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget

from ui.judges_tab import JudgesTab
from ui.categories_tab import CategoriesTab
from ui.groups_tab import GroupsTab
from ui.districts_tab import DistrictsTab
from ui.teams_tab import TeamsTab
from ui.participants_tab import ParticipantsTab
from ui.ships_tab import ShipsTab


class CompetitionPage(QWidget):
    def __init__(self, app_window):
        super().__init__()

        self.app_window = app_window

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setFixedWidth(100)

        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()

        self.tabs = QTabWidget()

        self.judges_tab = JudgesTab(app_window)
        self.categories_tab = CategoriesTab(app_window)
        self.groups_tab = GroupsTab(app_window)
        self.districts_tab = DistrictsTab(app_window)
        self.teams_tab = TeamsTab(app_window)
        self.participants_tab = ParticipantsTab(app_window)
        self.ships_tab = ShipsTab(app_window)

        self.tabs.addTab(self.judges_tab, "Судьи")
        self.tabs.addTab(self.categories_tab, "Категории")
        self.tabs.addTab(self.groups_tab, "Группы")
        self.tabs.addTab(self.districts_tab, "Районы")
        self.tabs.addTab(self.teams_tab, "Команды")
        self.tabs.addTab(self.participants_tab, "Участники")
        self.tabs.addTab(self.ships_tab, "Судна")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout = QVBoxLayout()
        layout.addLayout(back_layout)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def update_page(self):
        self.judges_tab.load_judges()
        self.categories_tab.load_categories()
        self.groups_tab.load_groups()
        self.districts_tab.load_districts()
        self.teams_tab.load_teams()
        self.participants_tab.load_filter_values()
        self.participants_tab.load_participants()
        self.ships_tab.load_filter_values()
        self.ships_tab.load_ships()

    def on_tab_changed(self, index):
        current_widget = self.tabs.widget(index)

        if hasattr(current_widget, "reset_mode"):
            current_widget.reset_mode()

        if hasattr(current_widget, "load_groups"):
            current_widget.load_groups()

        if hasattr(current_widget, "load_categories"):
            current_widget.load_categories()

        if hasattr(current_widget, "load_districts"):
            current_widget.load_districts()

    def go_back(self):
        self.app_window.show_select_page()
