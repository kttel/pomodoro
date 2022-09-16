import sqlite3
from datetime import datetime


class DB:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("sessions.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ses_list (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data_created TEXT,
        time_work INTEGER,
        time_free INTEGER)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        statement TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES ses_list(id))""")

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM ses_list")
        return self.cursor.fetchall()

    def get_one(self, ses_id: int) -> list:
        self.cursor.execute(f"SELECT * FROM ses_list WHERE id = {ses_id}")
        return list(map(list, self.cursor.fetchall()))

    def get_time(self, ses_id: int) -> str:
        self.cursor.execute(f"SELECT time_work, time_free FROM ses_list WHERE id = {ses_id}")
        return ''.join("{}".format(*self.cursor.fetchall()).strip('()').split(','))

    def get_task(self, ses_id: int) -> str:
        self.cursor.execute(f"SELECT statement FROM tasks where session_id = {ses_id}")
        result = self.cursor.fetchone()
        if result:
            return "{}".format(*result)
        return ''

    def update_task(self, ses_id: int, text: str) -> None:
        if not self.get_task(ses_id):
            self.cursor.execute(f'INSERT INTO tasks (session_id, statement) VALUES ({ses_id}, \'{text}\')')
            self.conn.commit()
        else:
            self.cursor.execute(f"UPDATE tasks SET statement = '{text}' WHERE session_id = {ses_id}")
            self.conn.commit()

    def create_session(self, name: str, periods: list) -> None:
        try:
            self.cursor.execute(f"""INSERT INTO ses_list (name, data_created, time_work, time_free) 
            VALUES ('{name}', '{datetime.now().strftime("%d.%m.%Y")}', {periods[0]}, {periods[1]});""")
            self.conn.commit()
        except Exception as error:
            print(f"Error occurred: {error}")

    def delete_session(self, ses_id: int) -> None:
        try:
            self.cursor.execute(f"DELETE FROM ses_list WHERE id={ses_id}")
            self.conn.commit()
        except Exception as error:
            print(f"Error occurred: {error}")

    def exit(self) -> None:
        self.conn.close()