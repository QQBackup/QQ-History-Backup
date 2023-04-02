class MessageHandler:
    _instance = None
    def __new__(cls, *args, **kw):  # Singleton
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    typeList: dict = {}
    @classmethod
    def register(cls, type_processor): # 注册 msgtype
        for msg_type in type_processor.support_msgtypes:
            if msg_type in cls.typeList:
                raise ValueError(f"重复定义了 msgtype {msg_type}")
            cls.typeList.update({msg_type: type_processor})
        return type_processor

    def get_all_types(self):
        return self.typeList
