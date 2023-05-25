import sqlite3
from typing import List

from app.Chat import Friend
from ..BaseImporter import BaseImporter
from ..ImporterManager import ImporterManager
from app.Database import _SingleDatabase
import os
from app.Log import Log
log = Log().logger
@ImporterManager.register

class android_qq(BaseImporter):
    pretty_name: str = "importer.android_qq"
    decrypt_key: str = ""

    def get_db_main(self) -> str:
        return os.path.join(self.config.get("ImportPath"), f"{self.config.get('QqNumber')}.db")

    def get_db_slowtable(self) -> str:
        return os.path.join(self.config.get("ImportPath"), f"slowtable_{self.config.get('QqNumber')}.db")

    def get_kc(self) -> str:
        return os.path.join(self.config.get("ImportPath"), f"kc")

    def init_db(self) -> None:
        self.dbs.add(self.get_db_main())
        self.dbs.add(self.get_db_slowtable(), allow_non_exist=True)
    
    def detect_percent_of_import(self, config) -> int:
        percent = 0
        if os.path.exists(self.get_db_main()):
            percent += 33
        if os.path.exists(self.get_db_slowtable()):
            percent += 33
        if os.path.exists(self.get_kc()):
            percent += 33
        else:
            # TODO: 从数据库中获取密钥
            log.warning("未找到密钥文件，无法解密数据库")
        try:
            db = _SingleDatabase(self.get_db_main())
            try:
                db.execute("select troopRemark from TroopInfoV2")
            except sqlite3.OperationalError:
                percent -= 5 # TIM
        except sqlite3.OperationalError:
            percent -= 10000 # 都打不开数据库了怎么解析？
        return percent
    
    def init_key(self) -> None:
        with open(self.get_kc(), "r") as f:
            self.decrypt_key = f.read().strip()

    def get_friend_list(self) -> List[Friend]:
         # TODO