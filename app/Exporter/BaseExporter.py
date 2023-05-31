from app.Config.ConfigManager import Config
from app.Chat import Friend, Group, Chat
from typing import List


class BaseExporter:
    pretty_name: str = "exporter.template"

    def __init__(self, config: Config):
        self.config: Config = config

    def __repr__(self) -> str:
        return (
            f"<Exporter: {self.pretty_name}({self.__class__.__name__})>"
        )
    
    def export(self, chat: Chat):
        """
        导出特定聊天
        """
        raise NotImplementedError
    
    def generate_table_of_content(self):
        """
        生成导出文件的目录
        """
        raise NotImplementedError
