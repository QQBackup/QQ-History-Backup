from typing import Type, Dict
from app.Const import Singleton


class MessageHandler(Singleton):
    typeList: Dict[int, Type] = {}

    @classmethod
    def register(cls, type_processor: Type) -> Type:
        """
        注册 msgtype
        """
        for msg_type in type_processor.support_msgtypes:
            if msg_type in cls.typeList:
                raise ValueError(f"重复定义了 msgtype {msg_type}")
            cls.typeList.update({msg_type: type_processor})
        return type_processor

    def get_all_types(self) -> Dict[int, Type]:
        """
        获取当前所有的 msgtype
        """
        return self.typeList
