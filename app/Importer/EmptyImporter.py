import sqlite3
from typing import List
import os

from app.Chat import Friend, Group
from .BaseImporter import BaseImporter
from .ImporterManager import ImporterManager
from app.Database import _SingleDatabase
from app.Message.BaseMessage import BaseMessage
from app.Log import log


@ImporterManager.register
class EmptyImporter(BaseImporter):
    pretty_name: str = "importer.empty"

    def init_db(self) -> None:
        pass

    def get_friend_list(self) -> List[Friend]:
        return []

    def get_group_list(self) -> List[Group]:
        return []

    def get_friend_message(self) -> List[BaseMessage]:
        raise NotImplementedError

    def get_group_message(self) -> List[BaseMessage]:
        raise NotImplementedError

    @classmethod
    def detect_possibility_of_import(cls, config) -> int:
        return -100000
