from app.Chat import Chat
from .BaseExporter import BaseExporter
from .ExporterManager import ExporterManager


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
