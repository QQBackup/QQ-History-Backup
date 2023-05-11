from os.path import join as path_join, isfile as path_isfile
class AssetsManager:
    """
    获取assets所在路径
    """

    assets_path: str = None
    @classmethod
    def init_assets(self):
        """
        初始化assets路径
        """
        if self.assets_path is not None:
            return
        self.assets_path = "assets"
        # TODO

    @classmethod
    def get_assets(self, *arg) -> str:
        """
        获取assets下的文件
        """
        self.init_assets()
        file_path = path_join(self.assets_path, *arg)
        if path_isfile(file_path):
            return file_path
        else:
            raise FileNotFoundError(file_path)
