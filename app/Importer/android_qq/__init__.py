import sqlite3
from ..BaseImporter import BaseImporter
from ..ImporterManager import ImporterManager
from app.Database import _SingleDatabase
import os
@ImporterManager.register
class android_qq(BaseImporter):
    pretty_name: str = "importer.android_qq"

    def get_db_main(self) -> str:
        return os.path.join(self.config.get("ImportPath"), f"{self.config.get('QqNumber')}.db")

    def get_db_slowtable(self) -> str:
        return os.path.join(self.config.get("ImportPath"), f"slowtable_{self.config.get('QqNumber')}.db")

    def init_db(self) -> None:
        self.dbs.add(self.get_db_main())
        self.dbs.add(self.get_db_slowtable(), allow_non_exist=True)
    
    def detect_percent_of_import(self, config) -> int:
        percent = 0
        if os.path.exists(self.get_db_main()):
            percent += 33
        if os.path.exists(self.get_db_slowtable()):
            percent += 33
        try:
            db = _SingleDatabase(self.get_db_main())
            db.execute("select troopRemark from TroopInfoV2")
        except sqlite3.OperationalError:
            percent -= 200 # TIM
        return percent
