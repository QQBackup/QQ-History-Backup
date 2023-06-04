from typing import List, Union

from app.Database import MultiDatabase
from app.Config.ConfigManager import Config
from app.Chat import Friend, Group
from app.Message.BaseMessage import BaseMessage


class BaseImporter:
    """
    导入器的基类，用于定义导入某个目录的接口
    """
    pretty_name: str = "importer.template"

    def __init__(self, config: Config):
        self.dbs: MultiDatabase = MultiDatabase()
        self.config: Config = config
        self.init_db()
        self.init_key()

    def init_db(self) -> None:
        """
        加载数据库、初始化相关变量
        """
        raise NotImplementedError

    def get_friend_list(self) -> List[Friend]:
        """
        获取好友列表以及扫描到的好友信息
        """
        raise NotImplementedError

    def get_group_list(self) -> List[Group]:
        """
        获取群列表以及扫描到的群信息
        """
        raise NotImplementedError
    
    def get_friend_by_uin(self, uin: str) -> Friend:
        """
        获取好友对象
        """
        res = [i for i in self.get_friend_list() if i.uin == uin]
        if len(res) == 0:
            raise IndexError(f"找不到 QQ 号 为{uin}的好友")
        if len(res) > 1:
            raise IndexError(f"找到多个 QQ 号 为{uin}的好友？？？bug！ {res}")
        return res[0]
    
    def get_group_by_uin(self, uin: str) -> Group:
        """
        获取群聊对象
        """
        res = [i for i in self.get_group_list() if i.uin == uin]
        if len(res) == 0:
            raise IndexError(f"找不到 QQ 号 为{uin}的群聊")
        if len(res) > 1:
            raise IndexError(f"找到多个 QQ 号 为{uin}的群聊？？？bug！ {res}")
        return res[0]
    
    def get_chat_message(self, chat: Union[Friend,Group]) -> List[BaseMessage]:
        """
        获取某个聊天对象的消息
        """
        if isinstance(chat, Friend):
            return self.get_friend_message(chat)
        elif isinstance(chat, Group):
            return self.get_group_message(chat)
        else:
            raise TypeError(f"chat 参数必须是 Friend 或 Group 类型，而不是 {type(chat)}")

    def get_friend_message(self, friend: Friend) -> List[BaseMessage]:
        """
        获取某个好友的消息
        """
        raise NotImplementedError

    def get_group_message(self, group: Group) -> List[BaseMessage]:
        """
        获取某个群聊的消息
        """
        raise NotImplementedError

    @classmethod
    def detect_possibility_of_import(cls, config) -> int:
        """
        判断给定的目录有多少概率是可以导入的
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            f"<Importer: {self.pretty_name}({self.__class__.__name__}) dbs={self.dbs} >"
        )

    def init_key(self) -> None:
        """
        加载解密所需的密钥
        """
        pass
