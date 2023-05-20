from i18n import t
import os
class Config:
    """
    管理单次运行中的配置
    """
    all_config_list: list = [] # 能被用户设置的配置，在所有实例中共享
    config_list: list = None
    def __init__(self):
        self.config_list = [i() for i in self.all_config_list]
    
    def by_dict(self, dict_config: dict):
        """
        通过 dict 设置
        """
        for i in self.config_list:
            if i.__class__.__name__ in dict_config:
                i.parse(dict_config[i.__class__.__name__])

    def verify(self) -> bool:
        """
        验证配置是否正确
        """
        for i in self.config_list:
            if not i.verify():
                return False
        # check necessary group
        necessary_group = {}
        for i in self.config_list:
            if i.necessary_group is not None and i.necessary_group != NECESSARY_NEVER:
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
    
    def get_single_config(self, config_name: str):
        """
        获取配置实例
        """
        for i in self.config_list:
            if i.__class__.__name__ == config_name:
                return i
        return None
    
    def get(self, config_name: str):
        """
        获取配置实例的值
        """
        if self.get_single_config(config_name) is not None:
            return self.get_single_config(config_name).get()
        raise ValueError("Config not found: " + config_name)

    @classmethod
    def register(cls, config: SingleConfig):
        cls.all_config_list.append(config)
        return config


class DefaultConfig:
    pass

NECESSARY_NEVER = None
NECESSARY_ALWAYS = -1
NECESSARY_GROUPS_EXPORT_ALL = 1

class SingleConfig:
    pretty_name: str = "config.template"
    type_: object = object
    value = None
    default_value = None
    necessary_group: int = NECESSARY_NEVER # 标记是否为必要配置，如果为 None 则不是必要配置，如果为 -1 则始终是必要配置，否则对于每个不同的 necessary_group，只要有一个被配置即可。在Manager中会自动检查
    hidden: bool = False # 标记是否为隐藏配置，如果为 True 则不会在配置文件中显示；同时，未 register 的始终不显示。
    disabled: bool = False # 标记是否为禁用配置，如果为 True 则会显示为不可修改
    def parse(self, value: str):
        return self.set(self._parse(value))

    def set(self, value):
        self.value = value
        if not self.verify():
            raise ConfigError(self)
        return self

    def verify(self, new_value = None) -> bool:
        """
        公开函数，用于对设定值进行验证
        """
        value = self.get() if new_value is None else new_value
        if value is None:
            return True # necessary_group 放到别的地方验证
        if not type(value) == self.type_:
            return False
        if not self._verify(value):
            return False
        return True

    def _verify(self, value = None) -> bool:
        """
        内部实现逻辑，对输入值进行验证
        """
        return True

    def get_pretty_name(self) -> str:
        """
        获取配置的显示名
        """
        return t(self.pretty_name)
    
    def get(self) -> object:
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

class IntConfig(SingleConfig):
    type_: object = int
    def _parse(self, value: str):
        return int(value)

class OptionConfig(SingleConfig):
    type_: object = object
    match_table: dict = {}
    translatable: bool = False # 是否要对 key 在显示时进行翻译
    def parse(self, value):
        if value not in self.match_table.keys():
            raise OptionConfigError(self)
        return super().set(self.match_table[value])
    def _verify(self, value=None) -> bool:
        return super()._verify(value) and value in self.match_table.values()

class ListConfig(SingleConfig):
    type_: object = list
    match_list: list = []
    def parse(self, value: list):
        assert(type(value) == list)
        if any([True for i in value if i not in self.match_list]):
            raise ListConfigError(self)
        return super().set(value)
    def _verify(self, value=None) -> bool:
        return super()._verify(value) and value in self.match_list

class FileConfig(SingleConfig):
    type_: object = str
    def _verify(self) -> bool:
        return os.path.isfile(self.get())

class FolderConfig(SingleConfig):
    type_: object = str
    def _verify(self) -> bool:
        return os.path.isdir(self.get())

class BoolConfig(OptionConfig):
    type_: object = bool
    match_table: dict = {"True": True, "False": False, True: True, False: False}

class YesNoConfig(BoolConfig):
    translatable: bool = True
    match_table: dict = {"config.yes": True, "config.no": False}



@Config.register
class LanguageFallback(ListConfig):
    pretty_name = "config.language_fallback"
    default_value = ["zh_CN",]
    hidden = True
    necessary_group = NECESSARY_ALWAYS

@Config.register
class LanguageCustom(ListConfig):
    pretty_name = "config.language"
    default_value = ["zh_CN",] # 从前往后逐个覆盖,也就是越后面的越可能出现在最终的字符串列表中
    necessary_group = NECESSARY_ALWAYS

@Config.register
class ImportPath(FolderConfig):
    pretty_name = "config.import_path"
    default_value = None
    necessary_group = NECESSARY_ALWAYS

@Config.register
class QqNumber(IntConfig):
    pretty_name = "config.qq_number"
    default_value = None
    necessary_group = NECESSARY_ALWAYS
    def _verify(self, value=None) -> bool:
        if not super()._verify(value):
            return False
        if value is None:
            return False
        if len(value) < 1:
            return False
        if not value.isdigit():
            return False
        if value[0] == '0':
            return False
        return True

@Config.register
class ExportAll(BoolConfig):
    pretty_name = "config.export_all"
    default_value = False
    necessary_group = NECESSARY_GROUPS_EXPORT_ALL
    def update_other(self, config):
        return config.#TODO

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
    translatable = True
    match_table = {"config.chat_type.group": "group", "config.chat_type.friend": "friend", "config.chat_type.all": "all"}

@Config.register
class EmoticonVersion(OptionConfig):
    pretty_name = "config.emoticon_version"
    default_value = "new"
    necessary_group = NECESSARY_ALWAYS
    match_table = {"config.emoticon_version.old": "old", "config.emoticon_version.new": "new"}

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

@Config.register
class MergeImage(YesNoConfig):
    pretty_name = "config.merge_image"
    default_value = True
    necessary_group = NECESSARY_ALWAYS


class ConfigError(ValueError):
    def __init__(self, config: SingleConfig):
        self.message = f"ConfigError: {config.pretty_name} got {config.value}."

class OptionConfigError(ValueError):
    def __init__(self, config: OptionConfig):
        self.message = f"OptionConfigError: {config.pretty_name} got {config.value}, but expected one of {config.match_table.keys()}."

class ListConfigError(ValueError):
    def __init__(self, config: ListConfig):
        self.message = f"ListConfigError: {config.pretty_name} got {config.value}, but expected all in {config.match_list}."
