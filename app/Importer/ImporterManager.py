from app.Importer.BaseImporter import BaseImporter
from app.Const import Singleton
from typing import Dict, List, Type


class ImporterManager(Singleton):
    all_importer_list: List[Type[BaseImporter]] = []

    @classmethod
    def register(cls, importer: Type[BaseImporter]) -> Type[BaseImporter]:
        cls.all_importer_list.append(importer)
        return importer

    @classmethod
    def __repr__(cls):
        return "<ImporterManager: " + str(cls.all_importer_list) + ">"

    @classmethod
    def to_name_list(cls):
        return [i.__name__ for i in cls.all_importer_list]

    @classmethod
    def get(cls, name: str) -> Type[BaseImporter]:
        for i in cls.all_importer_list:
            if i.__name__ == name:
                return i
        raise ValueError("Importer not found: " + name)

    @classmethod
    def to_match_table(cls) -> Dict[str, Type[BaseImporter]]:
        return {i.__name__: i for i in cls.all_importer_list}

    @classmethod
    def to_display_table(cls) -> Dict[str, str]:
        return {i.pretty_name: i.__name__ for i in cls.all_importer_list}
