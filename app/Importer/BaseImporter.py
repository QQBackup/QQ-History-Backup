from app.Database import MultiDatabase
from app.Config.ConfigManager import Config
from app.Chat import Friend, Group
from app.Message.BaseMessage import BaseMessage
from typing import List


class BaseImporter:
    pretty_name: str = "importer.template"

    def __init__(self, config: Config):
        self.dbs: MultiDatabase = MultiDatabase()
        self.config: Config = config
        self.init_db()

    def init_db(self) -> None:
        raise NotImplementedError

    def get_friend_list(self) -> List[Friend]:
        raise NotImplementedError

    def get_group_list(self) -> List[Group]:
        raise NotImplementedError

    def get_friend_message(self) -> List[BaseMessage]:
        raise NotImplementedError

    def get_group_message(self) -> List[BaseMessage]:
        raise NotImplementedError

    @classmethod
    def detect_percent_of_import(cls, config) -> int:
        """
        判断给定的目录有多少概率是可以导入的
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            f"<Importer: {self.pretty_name}({self.__class__.__name__}) dbs={self.dbs} >"
        )
    
    def init_key(self) -> None:
        pass
