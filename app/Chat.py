from typing import Dict, List, Union


class Chat:
    uin: str = None  # QQ 号
    remark: str = None  # 你给聊天的备注
    nickname: str = None  # 聊天对象的自己取的昵称
    db_table_name: str = None  # 数据库中对应表的名字
    global_uin: Dict[str, "Chat"] = {}  # 用于全局缓存

    def get_avatar(self, path: str) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.uin} {self.nickname}>"

    @property
    def pretty_name(self) -> str:
        nickname = self.nickname
        if self.remark:
            nickname = self.remark
        return f"{nickname}({self.uin})"

    def __new__(cls, uin: str, is_global: bool = False) -> "Chat":
        if is_global:
            if uin not in cls.global_uin:
                cls.global_uin[uin] = super().__new__(cls)
            return cls.global_uin[uin]
        return super().__new__(cls)

    @classmethod
    def get(cls, uin: str) -> Union["Chat", None]:
        if uin in cls.global_uin:
            return cls.global_uin[uin]
        return None


class Friend(Chat):
    global_uin: Dict[str, "Friend"] = {}  # 用于全局缓存
    in_group_title: str = None  # 在当前处理的群里的头衔
    in_group_remark: str = None  # 在当前处理的群里的群内名字

    @property
    def pretty_name(self) -> str:
        nickname = self.nickname
        if self.remark:
            nickname = self.remark
        if self.in_group_remark:
            nickname = self.in_group_remark
        if self.in_group_title:
            nickname = f"({self.in_group_title}) {nickname}"
        return f"{nickname}({self.uin})"


class Group(Chat):
    global_uin: Dict[str, "Group"] = {}  # 用于全局缓存

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_list: List[Friend] = []  # 群成员列表
