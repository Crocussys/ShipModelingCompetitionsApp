from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QLabel,
    QSizePolicy,
    QCheckBox,
    QComboBox,
)

from database import (
    get_competition,
    get_competition_status_name,
    update_competition_status,
    COMPETITION_STATUSES,
    COMPETITION_STATUS_SETUP,
    COMPETITION_STATUS_REGISTRATION,
    COMPETITION_STATUS_PRIMARY_PROTOCOLS,
    COMPETITION_STATUS_SECONDARY_PROTOCOLS,
)

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

        self.advanced_mode_checkbox = QCheckBox("Расширенный режим")
        self.advanced_mode_checkbox.toggled.connect(self.update_page)

        back_layout = QHBoxLayout()
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()
        back_layout.addWidget(self.advanced_mode_checkbox)

        self.competition_name_label = QLabel()
        self.competition_name_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.status_title_label  = QLabel()
        self.status_title_label .setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_value_label = QLabel()

        self.next_status_button = QPushButton()
        self.next_status_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )
        self.next_status_button.clicked.connect(self.go_next_status)

        self.status_combo = QComboBox()

        for status_id, status_name in COMPETITION_STATUSES.items():
            self.status_combo.addItem(status_name, status_id)

        self.status_combo.currentIndexChanged.connect(self.change_status_from_combo)

        self.next_status_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        self.status_combo.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_title_label)
        status_layout.addWidget(self.status_value_label)
        status_layout.addWidget(self.status_combo)
        status_layout.addWidget(self.next_status_button)
        status_layout.addStretch()

        self.tabs = QTabWidget()

        self.judges_tab = JudgesTab(app_window)
        self.categories_tab = CategoriesTab(app_window)
        self.groups_tab = GroupsTab(app_window)
        self.districts_tab = DistrictsTab(app_window)
        self.teams_tab = TeamsTab(app_window)
        self.participants_tab = ParticipantsTab(app_window)
        self.ships_tab = ShipsTab(app_window)

        self.tab_titles = {
            self.groups_tab: "Группы",
            self.categories_tab: "Категории",
            self.districts_tab: "Районы",
            self.judges_tab: "Судьи",
            self.teams_tab: "Команды",
            self.participants_tab: "Участники",
            self.ships_tab: "Судна",
        }

        self.tabs.addTab(self.groups_tab, "Группы")
        self.tabs.addTab(self.categories_tab, "Категории")
        self.tabs.addTab(self.districts_tab, "Районы")
        self.tabs.addTab(self.judges_tab, "Судьи")
        self.tabs.addTab(self.teams_tab, "Команды")
        self.tabs.addTab(self.participants_tab, "Участники")
        self.tabs.addTab(self.ships_tab, "Судна")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout = QVBoxLayout()
        layout.addLayout(back_layout)
        layout.addWidget(self.competition_name_label)
        layout.addLayout(status_layout)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def update_page(self):
        self.update_competition_header()
        self.update_tabs_visibility()

        self.groups_tab.load_groups()
        self.categories_tab.load_categories()
        self.districts_tab.load_districts()
        self.judges_tab.load_judges()
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

    def update_competition_header(self):
        competition = get_competition(self.app_window.selected_competition_id)

        if competition is None:
            return

        _, name, status = competition

        self.current_status = status

        advanced_mode = self.advanced_mode_checkbox.isChecked()

        self.status_value_label.setVisible(not advanced_mode)
        self.next_status_button.setVisible(not advanced_mode and status != COMPETITION_STATUS_SECONDARY_PROTOCOLS)
        self.status_combo.setVisible(advanced_mode)

        self.status_combo.blockSignals(True)
        index = self.status_combo.findData(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        self.status_combo.blockSignals(False)

        self.competition_name_label.setText(name)
        self.status_value_label.setText(
            get_competition_status_name(status)
        )

        if not advanced_mode:
            if status == COMPETITION_STATUS_SETUP:
                self.next_status_button.setText("Перейти к регистрации")
                self.next_status_button.setVisible(True)

            elif status == COMPETITION_STATUS_REGISTRATION:
                self.next_status_button.setText("Перейти к первичным протоколам")
                self.next_status_button.setVisible(True)

            elif status == COMPETITION_STATUS_PRIMARY_PROTOCOLS:
                self.next_status_button.setText("Перейти ко вторичным протоколам")
                self.next_status_button.setVisible(True)

            else:
                self.next_status_button.setVisible(False)

    def go_next_status(self):
        competition_id = self.app_window.selected_competition_id
        competition = get_competition(competition_id)

        if competition is None:
            return

        _, _, status = competition

        if status >= COMPETITION_STATUS_SECONDARY_PROTOCOLS:
            return

        update_competition_status(competition_id, status + 1)

        self.update_page()

    def set_tab_visible(self, widget, visible: bool):
        index = self.tabs.indexOf(widget)

        if visible and index == -1:
            self.tabs.addTab(widget, self.tab_titles[widget])

        elif not visible and index != -1:
            self.tabs.removeTab(index)

    def update_tabs_visibility(self):
        if self.advanced_mode_checkbox.isChecked():
            for widget in self.tab_titles:
                self.set_tab_visible(widget, True)
            return
        
        status = self.current_status

        setup_tabs = [
            self.groups_tab,
            self.categories_tab,
            self.districts_tab,
            self.judges_tab,
        ]

        registration_tabs = [
            self.groups_tab,
            self.categories_tab,
            self.districts_tab,
            self.judges_tab,
            self.teams_tab,
            self.participants_tab,
            self.ships_tab,
        ]

        protocols_tabs = [
            self.judges_tab,
            self.teams_tab,
            self.participants_tab,
            self.ships_tab,
        ]

        if status == COMPETITION_STATUS_SETUP:
            visible_tabs = setup_tabs
        elif status == COMPETITION_STATUS_REGISTRATION:
            visible_tabs = registration_tabs
        else:
            visible_tabs = protocols_tabs

        for widget in self.tab_titles:
            self.set_tab_visible(widget, widget in visible_tabs)

    def change_status_from_combo(self):
        if not self.advanced_mode_checkbox.isChecked():
            return

        competition_id = self.app_window.selected_competition_id
        status = self.status_combo.currentData()

        if competition_id is None or status is None:
            return

        update_competition_status(competition_id, status)
        self.update_page()
