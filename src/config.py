from pathlib import Path
import configparser


CONFIG_PATH = Path("src/config.ini")


def get_database_path() -> Path:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Файл config.ini не найден")

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")

    db_path = config["database"]["path"]
    return Path(db_path)
