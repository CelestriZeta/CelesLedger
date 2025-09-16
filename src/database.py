import sqlite3
from typing import TypedDict, Annotated, Sequence


class Record(TypedDict):
    item: Annotated[str, "所购物品的名称"]
    cost: Annotated[float, "此次消费或进账的金额，消费记录为负值，进账为正值"]
    time: Annotated[str, "此次消费或进账发生的时间，以'YYYY-MM-DD'格式记载。请结合用户输入与当前时间，确定消费或进账发生的时间"]
    type: Annotated[str,
        """
        此条记录所属的类型，按照居民消费八大类分类，只能为以下几种：
        - 食品烟酒
        - 衣着
        - 居住
        - 生活用品及服务
        - 交通通信
        - 教育文化娱乐
        - 医疗保健
        - 其它用品及服务
        """
    ]
    subtype: Annotated[str, ":此条记录所属的，type所填分类下的子类型"]
    original_message: Annotated[str, "此条记录对应的用户消息原文"]

db_creation_script = """
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

class DBManager:
    def __init__(self, db_name="consumption_records.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute(db_creation_script)
            self.conn.commit()

    def add_record(self, record: Record):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO consumption_records (item, cost, time, type, subtype, original_message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (record["item"], record["cost"], record["time"], record["type"], record["subtype"], record["original_message"])
            )
            self.conn.commit()

    def fetch_all_records(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM consumption_records")
        return cursor.fetchall()

    def execute(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
        return cursor.fetchall()

    def clear(self):
        with self.conn:
            self.conn.execute("DELETE FROM consumption_records")
            self.conn.commit()

    def close(self):
        self.conn.close()


