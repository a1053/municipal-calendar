from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'municipal.sqlite3'
SCHEMA = ROOT / 'data' / 'schema.sql'

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA.read_text(encoding='utf-8'))
    return con
