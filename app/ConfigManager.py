from app.i18n import t, i18n
import os
from typing import Any
from app.Log import Log

NECESSARY_NEVER = None
NECESSARY_ALWAYS = -1
NECESSARY_GROUPS_EXPORT_ALL = 1


class SingleConfig:
    pretty_name: str = "config.template"
    type_: object = object
    value = None
    default_value = None
    necessary_group: int | None = NECESSARY_NEVER  # 标记是否为必要配置，如果为 None 则不是必要配置，如果为 -1 则始终是必要配置，否则对于每个不同的 necessary_group，只要有一个被配置即可。在Manager中会自动检查
    hidden: bool = False  # 标记是否为隐藏配置，如果为 True 则不会在配置文件中显示；同时，未 register 的始终不显示。
    disabled: bool = False  # 标记是否为禁用配置，如果为 True 则会显示为不可修改

    def parse(self, value: str):
        return self.set(self._parse(value))

    def set(self, value):
        self.value = value
        if not self.verify():
            raise ConfigError(self)
        return self

    def verify(self) -> bool:
        """
        公开函数，用于对设定值进行验证
        """
        value = self.get()
        if value is None:
            return True  # necessary_group 放到别的地方验证
        if not type(value) == self.type_:
            return False
        if not self._verify():
            return False
        return True

    def _verify(self) -> bool:
        """
        内部实现逻辑，对输入值进行验证
        """
        return True

    def get_pretty_name(self) -> str:
        """
        获取配置的显示名
        """
        return t(self.pretty_name)

    def get(self) -> Any:
        """
        获取配置的值
        """
        if self.value is None:
            return self.default_value
        return self.value

    def _parse(self, value: str):
        """
        内部实现逻辑，对输入值进行解析
        """
        return value

    def update_other(self, config):
        """
        用于在配置更新时更新其他配置
        """
        pass

    def disable(self):
        """
        禁用配置
        """
        self.disabled = True
        return self

    def enable(self):
        """
        启用配置
        """
        self.disabled = False
        return self

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.get_pretty_name()}={self.get().__repr__()}>"


class IntConfig(SingleConfig):
    type_: object = int

    def _parse(self, value: str):
        return int(value)


class OptionConfig(SingleConfig):
    type_: object = object
    match_table: dict = {}
    display_table: dict = (
        {}
    )  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 match_table 中的 "test" 映射后的值
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译

    def parse(self, value):
        return super().set(self.match_table[value])

    def _verify(self) -> bool:
        value = self.get()
        return super()._verify() and value in self.match_table.values()

    def set(self, value):
        self.value = value
        if not self.verify():
            raise OptionConfigError(self)
        return self


class ListConfig(SingleConfig):
    type_: object = list
    match_list: list | None = []  # 允许的取值，如果为 None 则不限制
    display_table: dict = {}  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 "test" 的值
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译

    def parse(self, value: list):
        return self.set(value)

    def _verify(self) -> bool:
        value: list = self.get()
        return super()._verify() and (
            (self.match_list is None)
            or (not any([True for i in value if i not in self.match_list]))
        )

    def set(self, value):
        self.value = value
        if not self.verify():
            raise ListConfigError(self)
        return self


class FileConfig(SingleConfig):
    type_: object = str

    def _verify(self) -> bool:
        return os.path.isfile(self.get())  # type: ignore


class FolderConfig(SingleConfig):
    type_: object = str

    def _verify(self) -> bool:
        return os.path.isdir(self.get())  # type: ignore


class BoolConfig(OptionConfig):
    type_: object = bool
    match_table: dict = {"True": True, "False": False, True: True, False: False}


class YesNoConfig(BoolConfig):
    match_table: dict = {"yes": True, "no": False}
    display_table: dict = {"config.yes": "yes", "config.no": "no"}
    translatable: bool = True


class Config:
    """
    管理单次运行中的配置
    """

    all_config_list: list[type] = []  # 能被用户设置的配置，在所有实例中共享
    config_list: list[SingleConfig] = []

    def __init__(self):
        self.config_list = [i() for i in self.all_config_list]

    def by_dict(self, dict_config: dict):
        """
        通过 dict 设置
        """
        for i in self.config_list:
            if i.__class__.__name__ in dict_config:
                i.parse(dict_config[i.__class__.__name__])
        return self

    def verify(self) -> bool:
        """
        验证配置是否正确
        """
        for i in self.config_list:
            if not i.disabled and not i.verify():
                return False
        # check necessary group
        necessary_group = {}
        for i in self.config_list:
            if (
                not i.disabled
                and i.necessary_group is not None
                and i.necessary_group != NECESSARY_NEVER
            ):
                if i.necessary_group not in necessary_group:
                    necessary_group[i.necessary_group] = False
                if i.get() is not None:
                    necessary_group[i.necessary_group] = True
        for i in necessary_group:
            if necessary_group[i] is False:
                return False
        return True

    def update(self, config):
        """
        根据另外一个 Config 实例更新
        """
        for i in self.config_list:
            for j in config.config_list:
                if i.__class__.__name__ == j.__class__.__name__:
                    i.set(j.get())
                    break

    def get_single_config(self, config_name: str) -> SingleConfig:
        """
        获取配置实例
        """
        for i in self.config_list:
            if i.__class__.__name__ == config_name:
                return i
        raise ValueError("Config not found: " + config_name)

    def get(self, config_name: str):
        """
        获取配置实例的值
        """
        return self.get_single_config(config_name).get()

    def set(self, config_name: str, value):
        """
        设置配置实例的值
        """
        config = self.get_single_config(config_name)
        ret = config.set(value)
        config.update_other(self)
        return ret

    @classmethod
    def register(cls, config: type):
        cls.all_config_list.append(config)
        return config

    def __repr__(self):
        return "<Config: " + str(self.config_list) + ">"


@Config.register
class LanguageCustom(ListConfig):
    pretty_name = "config.language"
    default_value = []  # 从前往后逐个覆盖,也就是越后面的越可能出现在最终的字符串列表中
    necessary_group = NECESSARY_ALWAYS
    match_list = i18n().get_all_available_languages()


@Config.register
class LanguageFallback(LanguageCustom):
    pretty_name = "config.language_fallback"
    default_value = [
        "zh_CN",
    ]
    hidden = True
    necessary_group = NECESSARY_ALWAYS


@Config.register
class ImportPath(FolderConfig):
    pretty_name = "config.import_path"
    default_value = None
    necessary_group = NECESSARY_ALWAYS


@Config.register
class QqNumber(SingleConfig):
    """
    用于储存自己的 QQ 号，字符串类型。
    """

    type_: object = str
    pretty_name = "config.qq_number"
    default_value = None
    necessary_group = NECESSARY_ALWAYS

    def _verify(self) -> bool:
        if not super()._verify():
            return False
        value = self.get()
        if value is None:
            return False
        if len(value) < 1:
            return False
        if not value.isdigit():
            return False
        if value[0] == "0":
            return False
        return True


@Config.register
class ExportAll(YesNoConfig):
    pretty_name = "config.export_all"
    default_value = False
    necessary_group = NECESSARY_GROUPS_EXPORT_ALL

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
    default_value = None
    necessary_group = NECESSARY_GROUPS_EXPORT_ALL


@Config.register
class ChatType(OptionConfig):
    pretty_name = "config.chat_type"
    default_value = "friend"
    necessary_group = NECESSARY_ALWAYS
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
    necessary_group = NECESSARY_ALWAYS
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
    necessary_group = NECESSARY_ALWAYS


@Config.register
class ExportImage(YesNoConfig):
    pretty_name = "config.export_image"
    default_value = True
    necessary_group = NECESSARY_ALWAYS

    def update_other(self, config):
        if self.get():
            config.get_single_config("MergeImage").enable()
        else:
            config.get_single_config("MergeImage").disable()


@Config.register
class MergeImage(YesNoConfig):
    pretty_name = "config.merge_image"
    default_value = True
    necessary_group = NECESSARY_ALWAYS


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
    necessary_group = NECESSARY_ALWAYS


class ConfigError(ValueError):
    def __init__(self, config: SingleConfig):
        self.message = f"ConfigError: {config.pretty_name} got {config.value}."

    def __str__(self) -> str:
        return self.message


class OptionConfigError(ValueError):
    def __init__(self, config: OptionConfig):
        self.message = f"OptionConfigError: {config.pretty_name} got {config.get()}, but expected one of {config.match_table.keys()}."

    def __str__(self) -> str:
        return self.message


class ListConfigError(ValueError):
    def __init__(self, config: ListConfig):
        self.message = f"ListConfigError: {config.pretty_name} got {config.get()}, but expected contained in {config.match_list}."

    def __str__(self) -> str:
        return self.message
