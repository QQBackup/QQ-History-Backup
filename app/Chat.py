from typing import Dict, List, Union


class Chat:
    """
    与特定对象的聊天
    """
    uin: Union[str, None] = None  # QQ 号
    remark: Union[str, None] = None  # 你给聊天的备注
    nickname: Union[str, None] = None  # 聊天对象的自己取的昵称
    db_table_name: Union[str, None] = None  # 数据库中对应表的名字
    global_uin: Dict[str, "Chat"] = {}  # 用于全局缓存

    def get_avatar(self, path: str) -> None:
        """
        把头像导出到指定目录
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(db={True if self.db_table_name else False}) {self.pretty_name}>"

    @property
    def pretty_name(self) -> str:
        """
        获取显示时的名字
        """
        nickname = self.nickname
        if self.remark:
            nickname = self.remark
        uin = self.uin
        if uin is None: # 从数据库表里面扫到的
            uin = self.db_table_name
        return f"{nickname}({uin})"

    def __new__(cls, uin: Union[str, None] = None, is_global: bool = False) -> "Chat":
        if is_global:
            if uin not in cls.global_uin:
                cls.global_uin[uin] = super().__new__(cls)
            return cls.global_uin[uin]
        ret = super().__new__(cls)
        ret.uin = uin
        return ret

    @classmethod
    def get(cls, uin: str) -> Union["Chat", None]:
        """
        以 uin 为索引获取 Chat 对象
        """
        if uin in cls.global_uin:
            return cls.global_uin[uin]
        return None

    @classmethod
    def get_by_db_table_name(cls, db_table_name: str) -> Union["Chat", None]:
        """
        以 db_table_name 为索引获取 Chat 对象
        """
        for chat in cls.global_uin.values():
            if chat.db_table_name == db_table_name:
                return chat
        return None
    
    def copy(self, chat: "Chat") -> "Chat":
        """
        复制一份聊天对象
        """
        chat = self.__class__()
        chat.uin = self.uin
        chat.remark = self.remark
        chat.nickname = self.nickname
        chat.db_table_name = self.db_table_name
        return chat


class Friend(Chat):
    """
    与好友的聊天
    """
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
        uin = self.uin
        if uin is None: # 从数据库表里面扫到的
            uin = self.db_table_name
        return f"{nickname}({uin})"


class Group(Chat):
    """
    群组中的聊天
    """
    global_uin: Dict[str, "Group"] = {}  # 用于全局缓存
    members: List[Friend] = []  # 群成员列表

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members = []
