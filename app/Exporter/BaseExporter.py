from app.Database import MultiDatabase
from app.Config.ConfigManager import Config
from app.Chat import Friend, Group
from app.Message.BaseMessage import BaseMessage
from typing import List


class BaseExporter:
    pretty_name: str = "exporter.template"

    def __init__(self, config: Config):
        self.dbs: MultiDatabase = MultiDatabase()
        self.config: Config = config

    def __repr__(self) -> str:
        return (
            f"<Exporter: {self.pretty_name}({self.__class__.__name__}) #TODO" # TODO
        )
