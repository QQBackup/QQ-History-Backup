from app.Importer.BaseImporter import BaseImporter
from typing import List, Type

class ImporterManager:
    all_importer_list: List[Type[BaseImporter]] = []
    
    @classmethod
    def register(cls, importer: Type[BaseImporter]):
        cls.all_importer_list.append(importer)
        return importer

    def __repr__(self):
        return "<ImportManager: " + str(self.all_importer_list) + ">"
