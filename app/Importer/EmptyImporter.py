from typing import List

from app.Chat import Friend, Group
from app.Message.BaseMessage import BaseMessage
from app.Const import IMPORTER_POSSIBLE
from .BaseImporter import BaseImporter
from .ImporterManager import ImporterManager


@ImporterManager.register
class EmptyImporter(BaseImporter):
    pretty_name: str = "importer.empty"

    def init_db(self) -> None:
        pass

    def get_friend_list(self) -> List[Friend]:
        return []

    def get_group_list(self) -> List[Group]:
        return []

    def get_friend_message(self, friend) -> List[BaseMessage]:
        return []

    def get_group_message(self, group) -> List[BaseMessage]:
        return []

    @classmethod
    def detect_possibility_of_import(cls, config) -> int:
        return IMPORTER_POSSIBLE.IMPOSSIBLE
