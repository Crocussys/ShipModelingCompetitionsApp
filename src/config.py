import sys
import os
from pathlib import Path
import configparser


if getattr(sys, "frozen", False):
    EXE_DIR = Path(sys.executable).parent
else:
    EXE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = EXE_DIR / "config.ini"
APP_NAME = "ShipModelingCompetitionsApp"


def get_database_path() -> Path:
    config = configparser.ConfigParser()

    if not CONFIG_PATH.exists():
        appdata = (
            Path(os.getenv("APPDATA"))
            / APP_NAME
        )
        appdata.mkdir(parents=True, exist_ok=True)

        default_db = appdata / "db.sqlite"

        config["database"] = {
            "path": str(default_db)
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            config.write(file)

    config.read(CONFIG_PATH, encoding="utf-8")

    db_path = Path(config["database"]["path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return db_path
