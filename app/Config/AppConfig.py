from typing import Type
import json
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from app.Const import ConfigError
from app.Const import (
    CONFIG_NECESSARY_NEVER,
    CONFIG_NECESSARY_ALWAYS,
    CONFIG_NECESSARY_GROUPS_EXPORT_ALL,
)
from app.Config.ConfigTemplate import (
    IntConfig,
    SingleConfig,
    ListConfig,
    FolderConfig,
    YesNoConfig,
    OptionConfig,
)
from app.Config.ConfigManager import Config
from app.Exporter.ExporterManager import ExporterManager
from app.Importer.ImporterManager import ImporterManager
from app.i18n import i18n
from app.Log import log


@Config.register
class LanguageCustom(ListConfig):
    pretty_name = "config.language"
    value = json.dumps([])  # 从前往后逐个覆盖,也就是越后面的越可能出现在最终的字符串列表中
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_list = i18n().get_all_available_languages()


@Config.register
class LanguageFallback(LanguageCustom):
    pretty_name = "config.language_fallback"
    value = json.dumps(
        [
            "zh_CN",
        ]
    )
    hidden = True
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class ImportPath(FolderConfig):
    pretty_name = "config.import_path"
    value = ""
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class QqNumber(SingleConfig):
    """
    用于储存自己的 QQ 号，字符串类型。
    """

    type_: Type = str
    pretty_name = "config.qq_number"
    value = ""
    necessary_group = CONFIG_NECESSARY_ALWAYS

    def _verify(self, value: str) -> None:
        if (len(value) < 1) or (not value.isdigit()) or (value[0] == "0"):
            raise ConfigError(self, value)


@Config.register
class ExportAll(YesNoConfig):
    pretty_name = "config.export_all"
    value = json.dumps(False)
    necessary_group = CONFIG_NECESSARY_GROUPS_EXPORT_ALL

    def update_other(self, config: Config):
        chatType = config.get_single_config("ChatType")
        chatId = config.get_single_config("ChatId")
        if self.get() is True:
            chatType.set("all")
            chatId.set("")
            chatId.disable()
        else:
            chatType.set("friend")
            chatType.enable()
            chatId.enable()
        return self


@Config.register
class ChatId(QqNumber):
    pretty_name = "config.chat_id"
    value = ""
    necessary_group = CONFIG_NECESSARY_GROUPS_EXPORT_ALL


@Config.register
class ChatType(OptionConfig):
    pretty_name = "config.chat_type"
    value = "friend"
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_table = {"group": "group", "friend": "friend", "all": "all"}
    display_table = {
        "config.chat_type.group": "group",
        "config.chat_type.friend": "friend",
        "config.chat_type.all": "all",
    }
    translatable = True


@Config.register
class EmoticonVersion(OptionConfig):
    pretty_name = "config.emoticon_version"
    value = "new"
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_table = {"old": "old", "new": "new"}
    display_table = {
        "config.emoticon_version.old": "old",
        "config.emoticon_version.new": "new",
    }
    translatable = True


@Config.register
class ExportVoice(YesNoConfig):
    pretty_name = "config.export_voice"
    value = json.dumps(True)
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class ExportImage(YesNoConfig):
    pretty_name = "config.export_image"
    value = json.dumps(True)
    necessary_group = CONFIG_NECESSARY_ALWAYS

    def update_other(self, config):
        if self.get():
            config.get_single_config("MergeImage").enable()
        else:
            config.get_single_config("MergeImage").disable()


@Config.register
class MergeImage(YesNoConfig):
    pretty_name = "config.merge_image"
    value = json.dumps(True)
    necessary_group = CONFIG_NECESSARY_ALWAYS





@Config.register
class LogLevel(OptionConfig):
    pretty_name = "config.log_level"
    value = "INFO"
    match_table = {
        "DEBUG": DEBUG,
        "INFO": INFO,
        "WARNING": WARNING,
        "ERROR": ERROR,
        "CRITICAL": CRITICAL,
    }
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class ThreadCount(IntConfig):
    pretty_name = "config.thread_count"
    value = "1"
    necessary_group = CONFIG_NECESSARY_ALWAYS

    def _verify(self, value: str) -> None:
        try:
            threads = int(value)
        except ValueError as exc:
            raise ConfigError(self, value) from exc
        if threads < 1:
            raise ConfigError(self, value)
        if threads > 16:
            log.warning(f"线程数过多：{value}")


@Config.register
class Importer(OptionConfig):
    pretty_name = "config.importer"
    value = "AutoDetectImporter"
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_table = ImporterManager.to_match_table()
    display_table = ImporterManager.to_display_table()


@Config.register
class Exporter(OptionConfig):
    pretty_name = "config.exporter"
    value = ""
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_table = ExporterManager.to_match_table()
    display_table = ExporterManager.to_display_table()


"""@Config.register
class DecryptKeys(ListConfig):
    hidden = True
    match_list = None
    pretty_name = "config.decrypt_key"
    value = "[]"
    necessary_group = CONFIG_NECESSARY_NEVER"""
