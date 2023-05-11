import sqlite3
import os
from typing import List, Tuple, Optional

class _SingleDatabase:
    path: str = ""
    conn: sqlite3.Connection = None
    cur: sqlite3.Cursor = None
    def __new__(cls, path: str, allow_non_exist: bool = False, *args, **kwargs):
        if not os.path.isfile(path):
            if allow_non_exist:
                return None
            raise FileNotFoundError("TODO")
        else:
            return super().__new__(cls)

    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cur()

    def query(self, *args, **kwargs):
        """执行查询语句，返回所有查询结果"""
        if self.cur:
            try:
                self.cur.execute(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if str(e).startswith('no such table'):
                    return []
                else:
                    raise e
            row = self.cur.fetchall()
            return row
        return []

    def commit(self):
        """提交更改"""
        if self.conn:
            self.conn.commit()

    def close(self):
        """关闭连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_tables(self) -> List[str]:
        """返回数据库中所有表的名称列表"""
        tables = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in tables]

class MultiDatabase:
    databases: List[_SingleDatabase] = []
    def __init__(self):
        self.databases = []

    def add(self, path: str, allow_non_exist: bool = False) -> None:
        """向数据库列表末尾添加一个_SingleDatabase对象"""
        db = _SingleDatabase(path, allow_non_exist=allow_non_exist)
        if db is not None:
            self.databases.append(db)

    def query(self, *args, **kwargs) -> List[Tuple]:
        """在所有数据库连接中执行查询并返回结果"""
        results = []
        for db in self.databases:
            res = db.query(*args, **kwargs)
            if res:
                results.extend(res)
        return results

    def commit(self) -> None:
        """提交更改到所有数据库连接"""
        for db in self.databases:
            db.commit()

    def close(self) -> None:
        """从所有数据库连接中关闭连接"""
        for db in self.databases:
            db.close()
