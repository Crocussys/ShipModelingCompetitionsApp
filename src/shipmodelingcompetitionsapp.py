import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from config import get_database_path
from database import ensure_database
from ui.main_window import MainWindow


def check_database_or_exit() -> bool:
    try:
        db_path = get_database_path()
    except Exception as error:
        QMessageBox.critical(
            None,
            "Ошибка конфигурации",
            f"Не удалось прочитать конфиг:\n\n{error}"
        )
        return False

    try:
        if ensure_database(create_if_missing=False):
            return True
    except Exception as error:
        QMessageBox.critical(
            None,
            "Ошибка базы данных",
            f"Не удалось проверить структуру базы данных:\n\n{error}"
        )
        return False

    answer = QMessageBox.question(
        None,
        "База данных не найдена",
        f"База данных не найдена:\n\n{db_path}\n\n"
        "Инициализировать новую базу данных?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    if answer != QMessageBox.StandardButton.Yes:
        return False

    try:
        ensure_database(create_if_missing=True)
        return True
    except Exception as error:
        QMessageBox.critical(
            None,
            "Ошибка базы данных",
            f"Не удалось создать базу данных:\n\n{error}"
        )
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not check_database_or_exit():
        sys.exit(1)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
