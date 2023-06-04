import sqlite3
import os
from typing import Iterable, List, Tuple, Optional
from threading import Lock

from app.Log import log


class _SingleDatabase:
    def __new__(cls, path: str, allow_non_exist: bool = False, *args, **kwargs):
        if not os.path.isfile(path):
            if allow_non_exist:
                log.info("Database file not found, ignored: " + path)
                return None
            raise FileNotFoundError("Database file not found: " + path)
        else:
            return super().__new__(cls)

    def __init__(
        self,
        path: str,
        readonly: bool = False,
        check_same_thread: bool = True,
        *args,
        **kwargs,
    ):
        if (not readonly) and (not check_same_thread):
            raise ValueError("readonly must be True when check_same_thread is False")
        self.lock: Optional[Lock] = None
        if not check_same_thread:
            if sqlite3.threadsafety in (0, 1):
                self.lock = Lock()
        self.path: str = path
        self.conn: sqlite3.Connection = sqlite3.connect(
            path, check_same_thread=check_same_thread
        )
        self.check_same_thread = check_same_thread
        self.cur: sqlite3.Cursor = self.conn.cursor()

    def execute(self, *args, **kwargs):
        if self.lock:
            self.lock.acquire()
        ret = self.cur.execute(*args, **kwargs)
        if self.lock:
            self.lock.release()
        return ret

    def query(self, *args, **kwargs) -> Iterable[Tuple]:
        """执行查询语句，返回所有查询结果"""
        if self.lock:
            self.lock.acquire()
        if not self.check_same_thread:  # 多线程
            cur = self.conn.cursor()
        else:
            cur = self.cur
        self.cur.execute(*args, **kwargs)
        yield from self.cur.fetchall()
        if not self.check_same_thread:  # 多线程
            cur.close()
        if self.lock:
            self.lock.release()

    def commit(self) -> "_SingleDatabase":
        """提交更改"""
        if self.lock:
            with self.lock:
                self.conn.commit()
        else:
            self.conn.commit()
        return self

    def close(self) -> "_SingleDatabase":
        """关闭连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        return self

    def get_tables(self) -> Iterable[str]:
        """返回数据库中所有表的名称"""
        tables = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        for table in tables:
            yield table[0]

    def __repr__(self):
        return f"<_SingleDatabase {self.path}>"


class MultiDatabase:
    databases: List[_SingleDatabase] = []

    def __init__(self):
        self.databases = []

    def add(self, path: str, *args, **kwargs) -> "MultiDatabase":
        """向数据库列表末尾添加一个_SingleDatabase对象"""
        db = _SingleDatabase(path, *args, **kwargs)
        if db is not None:
            self.databases.append(db)
        return self

    def query(self, *args, **kwargs) -> Iterable[Tuple]:
        """在所有数据库连接中执行查询并返回结果"""
        for db in self.databases:
            try:
                yield from db.query(*args, **kwargs)
            except sqlite3.OperationalError as exc:
                if exc.args[0].startswith("no such table: "):
                    pass

    def commit(self) -> "MultiDatabase":
        """提交更改到所有数据库连接"""
        for db in self.databases:
            db.commit()
        return self

    def close(self) -> "MultiDatabase":
        """从所有数据库连接中关闭连接"""
        for db in self.databases:
            db.close()
        return self

    def get_tables(self) -> Iterable[str]:
        """返回所有数据库中的表"""
        for db in self.databases:
            yield from db.get_tables()

    def __repr__(self) -> str:
        return f"<MultiDatabase {self.databases}>"
