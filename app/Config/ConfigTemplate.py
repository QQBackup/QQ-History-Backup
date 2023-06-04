import os
from typing import Any, Dict, Optional, Type, Union
import json
from app.Const import (
    CONFIG_NECESSARY_NEVER,
    CONFIG_NECESSARY_ALWAYS,
    CONFIG_NECESSARY_GROUPS_EXPORT_ALL,
)
from app.Const import (
    ConfigError,
    OptionConfigError,
    ListConfigError,
    ConfigNecessaryError,
    BoolConfigError,
    FileConfigError,
    FolderConfigError,
)
from app.Const import UNSET
from app.i18n import t


class SingleConfig:
    pretty_name: str = "config.template"
    type_: Type = object
    value: str = ""  # 必须使用字符串输入，使用时再解析；同时也是默认值，绝对不能对该对象进行修改
    necessary_group: Optional[
        int
    ] = CONFIG_NECESSARY_NEVER  # 标记是否为必要配置，如果为 None 则不是必要配置，如果为 -1 则始终是必要配置，否则对于每个不同的 necessary_group，只要有一个被配置即可。在Manager中会自动检查
    hidden: bool = False  # 标记是否为隐藏配置，如果为 True 则不会在配置文件中显示；同时，未 register 的始终不显示。
    disabled: bool = False  # 标记是否为禁用配置，如果为 True 则会显示为不可修改
    temp_parsed_value = UNSET  # 临时存储解析后的值，用于 get

    def set(self, value: str, no_check: bool = False) -> "SingleConfig":
        if not no_check:
            self.verify(value=value)
        self.value = value
        self.temp_parsed_value = UNSET
        return self

    def str_to_value(self, str_input: str) -> Any:
        """
        处理用户输入的字符串，返回相对应的配置值。可以丢出异常。
        :param str_input: 用户输入的字符串
        """
        return str_input

    def verify(self, **kwargs) -> None:
        """
        公开函数，用于对已解析的设定值进行验证。
        若验证失败，会抛出异常。
        """
        if self.disabled:
            return
        value = kwargs.get("value", self.value)
        if value == "":
            if self.necessary_group == CONFIG_NECESSARY_ALWAYS:
                raise ConfigNecessaryError(self, value)
            return  # necessary_group 放到别的地方验证
        # if not type(value) == self.type_:
        #     raise ConfigError(self, value)
        self._verify(value)  # type: ignore
        return

    def _verify(self, value: str) -> None:
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
        if self.temp_parsed_value is UNSET:
            self.temp_parsed_value = self.str_to_value(self.value)
        return self.temp_parsed_value

    def update_other(self, config) -> "SingleConfig":
        """
        用于在配置更新时更新其他配置
        """
        return self

    def disable(self) -> "SingleConfig":
        """
        禁用配置
        """
        self.disabled = True
        return self

    def enable(self) -> "SingleConfig":
        """
        启用配置
        """
        self.disabled = False
        return self

    def __repr__(self) -> str:
        return f"<{self.get_pretty_name()}({self.__class__.__name__}) value={self.value.__repr__()}>"

    def dump(self) -> str:
        """
        用于将当前配置转换为字符串，若未设置，返回默认值
        """
        return self.value


class IntConfig(SingleConfig):
    type_: Type = int

    def str_to_value(self, str_input: str) -> int:
        try:
            ret = int(str_input)
        except ValueError as exc:
            raise ConfigError(self, str_input) from exc
        return ret


class OptionConfig(SingleConfig):
    type_: Type = object
    match_table: Dict[str, Any] = {}
    display_table: Dict[
        str, str
    ] = {}  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 match_table 中的 "test" 映射后的值。注意，不一定所有 Option 均有对应的 display_table，如果没有则不显示
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译

    def str_to_value(self, str_input: str) -> Any:
        if str_input not in self.match_table:
            raise OptionConfigError(self, str_input)
        return self.match_table[str_input]

    def _verify(self, value: str) -> None:
        if value not in self.match_table:
            raise OptionConfigError(self, value)


class ListConfig(SingleConfig):
    type_: Type = list
    match_list: Optional[list] = []  # 允许的取值，如果为 None 则不限制
    display_table: Dict[
        str, str
    ] = {}  # 显示时应当以什么名字显示，如 {"ui.test": "test"} 就表示该名字的选项值为 "test" 的值
    translatable: bool = True  # 是否要对 display_table 的 key 在显示时进行翻译

    def str_to_value(self, str_input: str) -> list:
        try:
            value = json.loads(str_input)
        except json.JSONDecodeError as exc:
            raise ListConfigError(self, str_input) from exc
        if not isinstance(value, list):
            raise ListConfigError(self, value)
        return value

    def _verify(self, value: str) -> None:
        parsed_list = self.str_to_value(value)
        if not (
            (self.match_list is None)
            or (not any([True for i in parsed_list if i not in self.match_list]))
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
    match_table: Dict[str, bool] = {"true": True, "false": False}

    def str_to_value(self, str_input: str) -> bool:
        str_input = str_input.lower()
        if str_input in self.match_table:
            return self.match_table[str_input]
        raise BoolConfigError(self, str_input)


class YesNoConfig(BoolConfig):
    match_table: Dict[str, bool] = {"yes": True, "no": False, "true": True, "false": False}
    display_table: Dict[str, str] = {"config.yes": "yes", "config.no": "no"}
    translatable: bool = True
