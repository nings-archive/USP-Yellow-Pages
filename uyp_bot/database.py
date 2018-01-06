from datetime import datetime
import sqlite3
from settings import FILENAME_DB

class Connection:
    def __init__(self):
        self.conn = sqlite3.connect(FILENAME_DB)
        self.curs = self.conn.cursor()
        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS mods (
                code        TEXT NOT NULL PRIMARY KEY, 
                renew_date  TEXT NOT NULL, 
                remove_date TEXT NOT NULL, 
                admin       TEXT NOT NULL, 
                url         TEXT NOT NULL UNIQUE);
        ''')
        self.conn.commit()

    def get_mod(self, mod):
        self.curs.execute('''
            SELECT * FROM mods WHERE code = ?;
            ''', (mod,) 
        )
        return self.curs.fetchone()

    def add_mod(self, code, renew_date, remove_date, admin, url):
        self.curs.execute('''
            INSERT INTO mods VALUES (?, ?, ?, ?, ?);
            ''', (code, renew_date, remove_date, admin, url)
        )
        self.conn.commit()
