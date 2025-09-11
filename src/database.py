import sqlite3

class db_manager:
    def __init__(self, db_name="../consumption_records.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consumption_records
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT,
                    cost REAL,
                    time TEXT,
                    type TEXT,
                    subtype TEXT,
                    original_message TEXT
                )
                """
            )
            self.conn.commit()

    def add_record(self, item, cost, time, type, subtype, original_message):
        with self.conn:
            self.conn.execute("""
                INSERT INTO consumption_records (item, cost, time, type, subtype, original_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item, cost, time, type, subtype, original_message))
            self.conn.commit()

    def fetch_records(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM consumption_records")
        return cursor.fetchall()

    def execute(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        return self

    def clear(self):
        with self.conn:
            self.conn.execute("DELETE FROM consumption_records")
            self.conn.commit()

    def close(self):
        self.conn.close()

