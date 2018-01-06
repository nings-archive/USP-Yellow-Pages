from datetime import datetime
import sqlite3
from settings import FILENAME_DB

class Connection:
    def __init__(self):
        # python-telegram-bot uses threading, does not play well w/ sqlite3
        self.conn = sqlite3.connect(FILENAME_DB, check_same_thread=False)
        self.curs = self.conn.cursor()
        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS mods (
                code        TEXT NOT NULL PRIMARY KEY, 
                renew_date  TEXT NOT NULL, 
                remove_date TEXT NOT NULL, 
                admin       TEXT NOT NULL, 
                url         TEXT NOT NULL UNIQUE);
        ''')
        self.curs.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id          TEXT NOT NULL PRIMARY KEY, 
                state       TEXT);
        ''')
        self.conn.commit()

    def get_mod(self, mod):
        self.curs.execute('''
            SELECT * FROM mods WHERE code = ?;
            ''', (mod,) 
        )
        return self.curs.fetchone()

    def get_user(self, user):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        row = self.curs.fetchone()
        # if user not exist, create
        if row is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?);
                ''', (user, None)
            )
            self.conn.commit()
            return (user, None)
        else:
            return row

    def update_user(self, user, state):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        # if user not exist, create
        if row is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?);
                ''', (user, state)
            )
            self.conn.commit()
        else:
            self.curs.execute('''
                UPDATE users SET state = ? WHERE id = ?
                ''', (state, user)
            )

    def add_mod(self, code, renew_date, remove_date, admin, url):
        self.curs.execute('''
            INSERT INTO mods VALUES (?, ?, ?, ?, ?);
            ''', (code, renew_date, remove_date, admin, url)
        )
        self.conn.commit()

    def add_user(self, user):
        self.curs.execute('SELECT * FROM users WHERE id = ?;', (user,))
        # only INSERT if not exist
        if self.curs.fetchone() is None:
            self.curs.execute('''
                INSERT INTO users VALUES (?, ?);
                ''', (user, None)
            )
            self.conn.commit()
