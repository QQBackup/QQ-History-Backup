import os
from app.Const import UNSET, NOT_PROVIDED
from app.Const import CONFIG_NECESSARY_NEVER, CONFIG_NECESSARY_ALWAYS, CONFIG_NECESSARY_GROUPS_EXPORT_ALL
from app.Const import ConfigError, OptionConfigError, ListConfigError, OptionConfigKeyError, ConfigNecessaryError, BoolConfigError, FileConfigError, FolderConfigError
from i18n import t
from typing import Any, Optional, Type
import json

class SingleConfig:
    pretty_name: str = "config.template"
    type_: Type = object
    value = UNSET
    default_value = UNSET
    necessary_group: Optional[int] = CONFIG_NECESSARY_NEVER  # 标记是否为必要配置，如果为 None 则不是必要配置，如果为 -1 则始终是必要配置，否则对于每个不同的 necessary_group，只要有一个被配置即可。在Manager中会自动检查
    hidden: bool = False  # 标记是否为隐藏配置，如果为 True 则不会在配置文件中显示；同时，未 register 的始终不显示。
    disabled: bool = False  # 标记是否为禁用配置，如果为 True 则会显示为不可修改

    def parse_str(self, str_input: str, no_check: bool = False):
        """
        处理用户输入的字符串，
        """
        return self.set(self.str_to_value(str_input), no_check=no_check)

    def set(self, value, no_check: bool = False):
        if not no_check:
            self.verify(value)
        self.value = value
        return self
    
    def str_to_value(self, str_input: str):
        """
        处理用户输入的字符串，返回相对应的配置值。可以丢出异常。
        :param str_input: 用户输入的字符串
        """
        return str_input


    def verify(self, value=UNSET) -> None:
        """
        公开函数，用于对已解析的设定值进行验证。
        若验证失败，会抛出异常。
        """
        if value is UNSET:
            value = self.get()
        if value is UNSET:
            if self.necessary_group == CONFIG_NECESSARY_ALWAYS:
                raise ConfigNecessaryError(self)
            return  # necessary_group 放到别的地方验证
        if not type(value) == self.type_:
            raise ConfigError(self, value)
        self._verify(value)
        return
    
    def _verify(self, value) -> None:
        """
        内部函数，用于对已解析的设定值进行验证。
        若验证失败，会抛出异常。
        """
        return

    def get_pretty_name(self) -> str:
        """
        获取配置的显示名
        """
        return t(self.pretty_name)

    def get(self) -> Any:
        """
        获取配置的值
        """
        if self.value is UNSET:
            return self.default_value
        return self.value

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
    type_: Type = int

    def str_to_value(self, str_input: str) -> int:
        return int(str_input)


class OptionConfig(SingleConfig):
    type_: Type = object
    match_table: dict = {}
    display_table: dict = (
        {}
    )  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 match_table 中的 "test" 映射后的值
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译


    def str_to_value(self, str_input: str):
        if str_input not in self.match_table.keys():
            raise OptionConfigKeyError(self, str_input)
        return self.match_table[str_input]

    def _verify(self, value):
        if value is not UNSET and value not in self.match_table.values():
            self.value = value
            raise OptionConfigError(self, value)


class ListConfig(SingleConfig):
    type_: Type = list
    match_list: Optional[list] = []  # 允许的取值，如果为 None 则不限制
    display_table: dict = {}  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 "test" 的值
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译

    def str_to_value(self, str_input: str) -> list:
        try:
            value = json.loads(str_input)
        except json.JSONDecodeError:
            raise ListConfigError(self, str_input)
        if not isinstance(value, list):
            raise ListConfigError(self, value)
        return value

    def _verify(self, value) -> None:
        if not (
            (self.match_list is None)
            or (not any([True for i in value if i not in self.match_list]))
        ):
            raise ListConfigError(self, value)


class FileConfig(SingleConfig):
    type_: Type = str

    def _verify(self, value: str) -> None:
        if not os.path.isfile(value):
            raise FileConfigError(self, value)


class FolderConfig(SingleConfig):
    type_: Type = str

    def _verify(self, value: str) -> None:
        if not os.path.isdir(value):
            raise FolderConfigError(self, value)


class BoolConfig(SingleConfig):
    type_: Type = bool
    match_table: dict = {"true": True, "false": False}
    def str_to_value(self, str_input: str):
        str_input = str_input.lower()
        if str_input in self.match_table.keys():
            return self.match_table[str_input]
        raise BoolConfigError(self, str_input)


class YesNoConfig(BoolConfig):
    match_table: dict = {"yes": True, "no": False}
    display_table: dict = {"config.yes": "yes", "config.no": "no"}
    translatable: bool = True
