import sqlite3
from typing import List, Dict
import os
from hashlib import md5

from app.Chat import Friend, Group
from app.Database import _SingleDatabase
from app.Log import log
from app.Const import IMPORTER_POSSIBLE
from ..BaseImporter import BaseImporter
from ..ImporterManager import ImporterManager
from .decrypt import AndroidQqDecrypt


@ImporterManager.register
class AndroidQq(BaseImporter):
    pretty_name: str = "importer.android_qq"
    decrypt_key: str = ""
    db_table_list: List[str] = []
    friends: List[Friend] = []
    groups: List[Group] = []
    group_members: Dict[
        int, List[Dict[int, List[str]]]
    ] = {}  # 根据 groopuin 分组的群成员列表，列表中参数详见 init_group_member_list
    decrypter: AndroidQqDecrypt = None
    tim_mode: bool = False

    def get_db_main(self) -> str:
        return os.path.join(
            self.config.get("ImportPath"), f"{self.config.get('QqNumber')}.db"
        )

    def get_db_slowtable(self) -> str:
        return os.path.join(
            self.config.get("ImportPath"), f"slowtable_{self.config.get('QqNumber')}.db"
        )

    def get_kc(self) -> str:
        return os.path.join(self.config.get("ImportPath"), "kc")

    def init_db(self) -> None:
        self.db_table_list = []
        self.friends = []
        self.groups = []
        self.group_members = {}
        try:
            self.dbs.add(self.get_db_main())
        except FileNotFoundError as exc:
            log.error(f"未找到主数据库文件 {self.get_db_main()}，无法导入")
            raise exc
        self.dbs.add(self.get_db_slowtable(), allow_non_exist=True)
        self.db_table_list = list(self.dbs.get_tables())

    @classmethod
    def detect_possibility_of_import(cls, config) -> int:
        percent = 0
        cls.config = config
        if os.path.exists(cls.get_db_main(self=cls)):
            percent += IMPORTER_POSSIBLE.FILE_FOUND
        else:
            return IMPORTER_POSSIBLE.IMPOSSIBLE
        if os.path.exists(cls.get_db_slowtable(self=cls)):
            percent += IMPORTER_POSSIBLE.FILE_FOUND
        if os.path.exists(cls.get_kc(self=cls)):
            percent += IMPORTER_POSSIBLE.KEY_FOUND
        try:
            db = _SingleDatabase(cls.get_db_main(self=cls))
            try:
                db.execute("select troopRemark from TroopInfoV2")
            except sqlite3.OperationalError:
                if not cls.tim_mode:
                    percent += IMPORTER_POSSIBLE.DOWNGRADE
            try:
                db.close()
            except sqlite3.OperationalError:
                pass
        except sqlite3.OperationalError:
            percent = IMPORTER_POSSIBLE.IMPOSSIBLE
        return percent

    def init_key(self) -> None:
        with open(self.get_kc(), "r", encoding="utf8") as f:
            self.decrypt_key = f.read().strip()
#        log.info(f"解密密钥为 {self.decrypt_key}")
        self.decrypter: AndroidQqDecrypt = AndroidQqDecrypt(self.decrypt_key)

    def get_friend_tablename(self, uin: str) -> str:
        return f"mr_friend_{md5(uin.encode('utf8'), usedforsecurity=False).hexdigest().upper()}_New"

    def get_group_tablename(self, uin: str) -> str:
        return f"mr_troop_{md5(uin.encode('utf8'), usedforsecurity=False).hexdigest().upper()}_New"

    def init_friend_list(self) -> None:
        if self.friends:
            return
        # uin-QQ号，remark-备注，name-昵称
        sql = "select uin,remark,name from Friends"
        for i in self.dbs.query(sql):
            uin, remark, name = i[0], i[1], i[2]
            decode_uin = self.decrypter.decrypt(uin)
            friend = Friend(uin=decode_uin, is_global=True)
            decode_remark = self.decrypter.decrypt(remark)
            decode_name = self.decrypter.decrypt(name)
            friend.uin = decode_uin
            friend.remark = decode_remark if decode_remark else None
            friend.nickname = decode_name if decode_name else None
            table_name = self.get_friend_tablename(decode_uin)
            if table_name not in self.db_table_list:
                pass
            #    log.warning(f"未找到好友 {decode_uin} 表 {table_name}")  # TODO:i18n
            else:
                friend.db_table_name = table_name
            self.friends.append(friend)

    def get_friend_list(self) -> List[Friend]:
        self.init_friend_list()
        return self.friends

    def init_group_member_list(self) -> None:
        if self.group_members:
            return
        sql = "SELECT troopuin, memberuin, autoremark, troopnick, friendnick, recommendRemark, mUniqueTitle FROM TroopMemberInfo"
        for row in self.dbs.query(sql):
            groupuin = self.decrypter.decrypt(row[0])
            memberuin = self.decrypter.decrypt(row[1])
            names = [self.decrypter.decrypt(i) for i in row[2 : 6 + 1]]
            # 2是你给好友的备注，3是好友的群昵称，4是好友名字，5是好友的群昵称，mUniqueTitle是群头衔
            # xxx 我不知道这个顺序怎么搞的 一部分是猜
            log.debug(f"names: {names}")
            self.group_members.setdefault(groupuin, {})
            self.group_members[groupuin].update({memberuin: names})

    def init_group_list(self) -> None:
        if self.groups:
            return
        # uin-QQ号，remark-备注，name-昵称
        sql = "select troopuin,troopname,troopRemark from TroopInfoV2"
        if self.tim_mode:
            sql = sql.replace(",troopRemark", "")  # TIM 模式下没有 troopRemark
        for i in self.dbs.query(sql):
            group = Group()
            uin, name = i[0], i[1]
            decode_uin = self.decrypter.decrypt(uin)
            decode_name = self.decrypter.decrypt(name)
            group.uin = decode_uin
            group.nickname = decode_name
            if not self.tim_mode:
                remark = i[2]
                decode_remark = self.decrypter.decrypt(remark)
                group.remark = decode_remark
            table_name = self.get_group_tablename(decode_uin)
            if table_name not in self.db_table_list:
                pass
#                log.warning(f"未找到群聊 {decode_uin} 表 {table_name}")  # TODO:i18n
            else:
                group.db_table_name = table_name
            # 获取群成员
            self.init_group_member_list()
            group_members = self.group_members.get(uin, {})
            for memberuin, names in group_members.items():
                # 你给好友的备注 好友的群昵称 好友名 好友的群昵称 群头衔
                member = Friend.get(memberuin).copy()
                if member is None:
                    member_db_name = self.get_friend_tablename(memberuin)
                    member_by_db_name = Friend.get_by_db_table_name(member_db_name)
                    if member_by_db_name is not None:
                        member = member_by_db_name
                        member.uin = memberuin
                        log.debug(f"Found chat hashed uin: {memberuin} -> {member_db_name}")
                    else:
                        member = Friend(uin=memberuin, is_global=False)
                member.in_group_title = names[4] if names[4] else None
                if names[3] != names[1]:
                    log.warning(f"群聊 {uin} 中 {memberuin} 的昵称不同！{names}")
                member.in_group_nickname = names[3] if names[3] else (names[1] if names[1] else None)
                if member.remark and member.remark != names[0]:
                    log.warning(f"群聊 {uin} 中 {memberuin} 的备注不同！{names}")
                member.remark = member.remark if member.remark else names[0]
                if member.nickname and member.nickname != names[2]:
                    log.warning(f"群聊 {uin} 中 {memberuin} 的昵称不同！{names}")
                member.nickname = member.nickname if member.nickname else names[2]
                group.members.append(member)
            self.groups.append(group)

    def get_group_list(self) -> List[Group]:
        self.init_group_list()
        return self.groups
