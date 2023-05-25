from app.Importer.BaseImporter import BaseImporter
from typing import List, Type
from app.Const import Singleton

class ImporterManager(Singleton):
    all_importer_list: List[Type[BaseImporter]] = []
    
    @classmethod
    def register(cls, importer: Type[BaseImporter]):
        cls.all_importer_list.append(importer)
        return importer

    @classmethod
    def __repr__(cls):
        return "<ImportManager: " + str(cls.all_importer_list) + ">"
    
    @classmethod
    def to_name_list(cls):
        return [i.__name__ for i in cls.all_importer_list]
    
    @classmethod
    def get(cls, name: str) -> BaseImporter:
        for i in cls.all_importer_list:
            if i.__name__ == name:
                return i
        raise ValueError("Importer not found: " + name)
