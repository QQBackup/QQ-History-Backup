import sqlite3
import os
from typing import List, Tuple, Optional
from app.Log import Log

log = Log().logger
from threading import Lock


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
        allow_non_exist: bool = False,
        readonly: bool = False,
        check_same_thread: bool = True,
        *args,
        **kwargs
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
        self.cur: sqlite3.Cursor = self.conn.cursor()
    
    def execute(self, *args, **kwargs) -> Optional[sqlite3.Cursor]:
        if self.lock:
            self.lock.acquire()
        ret = self.cur.execute(*args, **kwargs)
        if self.lock:
            self.lock.release()
        return ret

    def query(self, *args, **kwargs) -> List[Tuple]:
        """执行查询语句，返回所有查询结果"""
        if self.lock:
            self.lock.acquire()
        ret = self.cur.execute(*args, **kwargs)
        yield from self.cur.fetchall()
        if self.lock:
            self.lock.release()

    def query_new_cursor(self, *args, **kwargs) -> List[Tuple]:
        """使用单独的 cursor 执行查询语句，返回所有查询结果"""
        if self.lock:
            self.lock.acquire()
        cur = self.conn.cursor()
        cur.execute(*args, **kwargs)
        yield from cur.fetchall()
        cur.close()
        if self.lock:
            self.lock.release()


    def commit(self) -> None:
        """提交更改"""
        if self.lock:
            with self.lock:
                self.conn.commit()
        else:
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
    
    def __repr__(self):
        return f"<_SingleDatabase {self.path}>"


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

    def query_new_cursor(self, *args, **kwargs) -> List[Tuple]:
        """使用单独的 cursor 在所有数据库连接中执行查询并返回结果"""
        results = []
        for db in self.databases:
            res = db.query_new_cursor(*args, **kwargs)
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
    
    def __repr__(self):
        return f"<MultiDatabase {self.databases}>"
