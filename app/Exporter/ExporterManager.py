from app.Exporter.BaseExporter import BaseExporter
from typing import Dict, List, Type
from app.Const import Singleton

class ExporterManager(Singleton):
    all_exporter_list: List[Type[BaseExporter]] = []
    
    @classmethod
    def register(cls, exporter: Type[BaseExporter]):
        cls.all_exporter_list.append(exporter)
        return exporter

    @classmethod
    def __repr__(cls):
        return "<ExporterManager: " + str(cls.all_exporter_list) + ">"
    
    @classmethod
    def to_name_list(cls):
        return [i.__name__ for i in cls.all_exporter_list]
    
    @classmethod
    def get(cls, name: str) -> Type[BaseExporter]:
        for i in cls.all_exporter_list:
            if i.__name__ == name:
                return i
        raise ValueError("Exporter not found: " + name)
    
    @classmethod
    def to_match_table(cls) -> Dict[str, Type[BaseExporter]]:
        return {i.__name__: i for i in cls.all_exporter_list}
    
    @classmethod
    def to_display_table(cls) -> Dict[str, str]:
        return {i.pretty_name: i.__name__ for i in cls.all_exporter_list}
