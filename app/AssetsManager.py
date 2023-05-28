import os
from typing import List, Tuple
from app.Log import Log
import subprocess
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
    
    @classmethod
    def execute_asset(cls, *arg, args:list = [], encoding: str = "utf-8") -> Tuple[int, str, str]:
        """
        执行assets下的文件，返回执行结果（退出码、stdout、stderr）
        """
        cls.init_assets()
        file_path = os.path.join(cls.assets_path, *arg)
        if os.path.isfile(file_path):
            p = subprocess.Popen([file_path, *args], shell=False,stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ret = p.communicate()
        else:
            raise FileNotFoundError(file_path)
        return (p.returncode, ret[0].decode(encoding), ret[1].decode(encoding))
