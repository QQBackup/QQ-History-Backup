class Config:
    """
    管理单次运行中的配置
    """
    languages: list = [] # 从前往后解析
    def __init__(self):
        language_fallback = ["zh_CN",]
        language_custom = ["zh_CN",]
    def by_json(self, json: dict) -> bool:
        """
        通过json设置
        """
        pass
    def verify(self) -> bool:
        """
        验证配置是否正确
        """
        pass
    def update(self, config):
        pass

class DefaultConfig:
    pass

class SingleConfig:
    pretty_name: str = "config.template"
    type_: object = int
    value = None
    defaul_value = None
    def set(self, value):
        self.value = value

class DictConfig(SingleConfig):
    pretty_name: str = "config.template"
    type_: object = object
    value = None
    match_table: dict = {}
    def set(self, value):
        return super().set(self.match_table[value])
    # TODO:error raise

class ListConfig(DictConfig):
    pretty_name: str = "config.template"
    type_: object = object
    value = None
    match_list: list = []
    def set(self, value):
        return super().set(value)
    # TODO:error raise

class BoolConfig(DictConfig):
    pretty_name: str = "config.template"
    type_: object = bool
    value = None
    match_table: dict = {"True": True, "False": False}

class Language(ListConfig):
    pass