from app.Const import (
    CONFIG_NECESSARY_NEVER,
    CONFIG_NECESSARY_ALWAYS,
    CONFIG_NECESSARY_GROUPS_EXPORT_ALL,
)
import os
from typing import Any, Dict, List, Type, Union
from app.Log import Log
from app.Const import UNSET, NOT_PROVIDED
from app.Config.ConfigTemplate import SingleConfig


class Config:
    """
    管理单次运行中的配置
    """

    all_config_list: List[type] = []  # 能被用户设置的配置，在所有实例中共享
    config_list: List[SingleConfig] = []

    def __init__(self):
        self.config_list = [i() for i in self.all_config_list]

    def by_dict(self, dict_config: Dict[str, str]) -> 'Config':
        """
        通过未完成 str 解析的 dict 设置
        """
        for i in self.config_list:
            if i.__class__.__name__ in dict_config:
                i.parse_str(dict_config[i.__class__.__name__])
        return self

    def verify(self) -> bool:
        """
        验证配置是否正确
        """ # TODO: 重写
        for i in self.config_list:
            if not i.disabled and not i.verify():
                return False
        # check necessary group
        necessary_group = {}
        for i in self.config_list:
            if (
                not i.disabled
                and i.necessary_group is not None
                and i.necessary_group != CONFIG_NECESSARY_NEVER
            ):
                if i.necessary_group not in necessary_group:
                    necessary_group[i.necessary_group] = False
                if i.get() is not None:
                    necessary_group[i.necessary_group] = True
        for i in necessary_group:
            if necessary_group[i] is False:
                return False
        return True

    def update(self, config) -> 'Config':
        """
        根据另外一个 Config 实例更新
        """
        for i in self.config_list:
            for j in config.config_list:
                if i.__class__.__name__ == j.__class__.__name__:
                    i.set(j.get())
                    break
        return self

    def get_single_config(self, config_name: str) -> SingleConfig:
        """
        获取配置实例
        """
        for i in self.config_list:
            if i.__class__.__name__ == config_name:
                return i
        raise ValueError("Config not found: " + config_name)

    def get(self, config_name: str) -> Any:
        """
        获取配置实例的值
        """
        return self.get_single_config(config_name).get()

    def set(self, config_name: str, value) -> SingleConfig:
        """
        设置配置实例的值
        """
        config = self.get_single_config(config_name)
        ret = config.set(value)
        config.update_other(self)
        return ret

    def str_set(self, config_name: str, value: str) -> SingleConfig:
        """
        使用 str 设置配置实例的值
        """
        config = self.get_single_config(config_name)
        ret = config.parse_str(value)
        config.update_other(self)
        return ret

    @classmethod
    def register(cls, config: Type[SingleConfig]) -> Type[SingleConfig]:
        cls.all_config_list.append(config)
        return config

    def __repr__(self) -> str:
        return "<Config: " + str(self.config_list) + ">"
    
    def to_dict(self) -> Dict[str, Union[str, None]]:
        """
        将配置转换为 dict
        """
        return {i.__class__.__name__: i.dump() for i in self.config_list}
