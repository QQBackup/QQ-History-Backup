from app.Chat import Friend, Group, Chat
from .BaseExporter import BaseExporter
from .ExporterManager import ExporterManager
from app.Message.BaseMessage import BaseMessage
from app.Log import log


@ExporterManager.register
class EmptyExporter(BaseExporter):
    pretty_name: str = "exporter.empty"
    
    
    def export(self, chat: Chat):
        """
        导出特定聊天
        """
        pass
    
    def generate_table_of_content(self):
        """
        生成导出文件的目录
        """
        pass
