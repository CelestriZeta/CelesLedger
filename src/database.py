import sqlite3

class db_manager:

    def __init__(self):
        self.connection = sqlite3.connect("../consumption_records.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS consumption_records (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              item TEXT DEFAULT NULL,
              cost REAL DEFAULT NULL,
              time TEXT DEFAULT NULL,
              type TEXT DEFAULT NULL,
              subtype TEXT DEFAULT NULL,
              original_message TEXT DEFAULT NULL
            );
            """
        )
        self.connection.commit()

dbm = db_manager()
dbm.cursor.close()