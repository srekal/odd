import pathlib
import sqlite3


def get_db_conn(db_path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys;")
    return connection
