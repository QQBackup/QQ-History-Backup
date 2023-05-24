import os
from typing import List
from app.Log import Log
log = Log().logger

class AssetsManager:
    """
    获取assets所在路径
    """

    @classmethod
    def try_assets_path(cls, *args) -> bool:
        """
        尝试获取assets路径
        """
        if cls.assets_path is not None:
            return True
        if os.path.isdir(os.path.join(*args)):
            cls.assets_path = os.path.join(*args)
            log.debug("Assets path: " + cls.assets_path)
            return True
        else:
            return False

    @classmethod
    def init_assets(cls) -> None:
        """
        初始化assets路径
        """
        if cls.assets_path is not None:
            return
        abspath = os.path.abspath(__file__)
        possible_paths = [
            ("assets",),
            ("..", "assets"),
            (abspath, "assets"),
            (abspath, "..", "assets"),
        ]
        for i in possible_paths:
            if cls.try_assets_path(i):
                return
        raise FileNotFoundError("Assets not found! Tried " + str(possible_paths))

    @classmethod
    def get_assets(cls, *arg) -> str:
        """
        获取assets下的文件
        """
        cls.init_assets()
        file_path = os.path.join(cls.assets_path, *arg)
        if os.path.isfile(file_path):
            return file_path
        else:
            raise FileNotFoundError(file_path)

    @classmethod
    def list_assets(cls, *arg) -> List[str]:
        """
        获取assets下某个目录中的文件列表
        """
        cls.init_assets()
        dir_path = os.path.join(cls.assets_path, *arg)
        if os.path.isdir(dir_path):
            return os.listdir(dir_path)
        else:
            raise NotADirectoryError(dir_path)
