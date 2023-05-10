class Config:
    """
    管理单次运行中的配置
    """
    languages: list = [] # 从前往后解析
    def __init__(self):
        languages = ["zh_CN",]
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

