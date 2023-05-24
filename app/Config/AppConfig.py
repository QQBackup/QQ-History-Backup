from typing import Type
from app.Const import ConfigError
from app.Const import UNSET, NOT_PROVIDED
from app.Const import CONFIG_NECESSARY_NEVER, CONFIG_NECESSARY_ALWAYS, CONFIG_NECESSARY_GROUPS_EXPORT_ALL
from app.Config.ConfigTemplate import IntConfig, SingleConfig, ListConfig, FolderConfig, YesNoConfig, OptionConfig
from app.Config.ConfigManager import Config
from app.i18n import i18n
from app.Log import Log
log = Log().logger

@Config.register
class LanguageCustom(ListConfig):
    pretty_name = "config.language"
    default_value = []  # 从前往后逐个覆盖,也就是越后面的越可能出现在最终的字符串列表中
    necessary_group = CONFIG_NECESSARY_ALWAYS
    match_list = i18n().get_all_available_languages()


@Config.register
class LanguageFallback(LanguageCustom):
    pretty_name = "config.language_fallback"
    default_value = [
        "zh_CN",
    ]
    hidden = True
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class ImportPath(FolderConfig):
    pretty_name = "config.import_path"
    default_value = UNSET
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class QqNumber(SingleConfig):
    """
    用于储存自己的 QQ 号，字符串类型。
    """

    type_: Type = str
    pretty_name = "config.qq_number"
    default_value = UNSET
    necessary_group = CONFIG_NECESSARY_ALWAYS

    def _verify(self, value: str) -> None:
        if (len(value) < 1) or (not value.isdigit()) or (value[0] == "0"):
            raise ConfigError(self, value)
        


@Config.register
class ExportAll(YesNoConfig):
    pretty_name = "config.export_all"
    default_value = False
    necessary_group = CONFIG_NECESSARY_GROUPS_EXPORT_ALL

    def update_other(self, config: Config):
        chatType = config.get_single_config("ChatType")
        chatId = config.get_single_config("ChatId")
        if self.get() is True:
            chatType.set("all")
            chatId.set(chatId.default_value)
            chatId.disable()
        else:
            chatType.enable()
            chatId.enable()


@Config.register
class ChatId(QqNumber):
    pretty_name = "config.chat_id"
    default_value = UNSET
    necessary_group = CONFIG_NECESSARY_GROUPS_EXPORT_ALL


@Config.register
class ChatType(OptionConfig):
    pretty_name = "config.chat_type"
    default_value = "friend"
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
    default_value = "new"
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
    default_value = True
    necessary_group = CONFIG_NECESSARY_ALWAYS


@Config.register
class ExportImage(YesNoConfig):
    pretty_name = "config.export_image"
    default_value = True
    necessary_group = CONFIG_NECESSARY_ALWAYS

    def update_other(self, config):
        if self.get():
            config.get_single_config("MergeImage").enable()
        else:
            config.get_single_config("MergeImage").disable()


@Config.register
class MergeImage(YesNoConfig):
    pretty_name = "config.merge_image"
    default_value = True
    necessary_group = CONFIG_NECESSARY_ALWAYS


from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


@Config.register
class LogLevel(OptionConfig):
    pretty_name = "config.log_level"
    default_value = INFO
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
    default_value = 1
    necessary_group = CONFIG_NECESSARY_ALWAYS
    def _verify(self, value: int) -> None:
        if value < 1:
            raise ConfigError(self, value)
        if value > 16:
            log.warning(f"线程数过多：{value}")

@Config.register
class Importer(OptionConfig):
    pretty_name = "config.importer"
    default_value = #TODO
    necessary_group = CONFIG_NECESSARY_ALWAYS
@Config.register
class Exporter(OptionConfig):
    pretty_name = "config.exporter"
    default_value = #TODO
    necessary_group = CONFIG_NECESSARY_ALWAYS


