class FileManager:
    _instance = None
    def __new__(cls, *args, **kw):  # Singleton
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
