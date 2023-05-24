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
