from locale import getdefaultlocale
import json
from app.AssetsManager import AssetsManager
from app.ConfigManager import Config
class i18n():
    language_file: str = None
    translation_table: dict = {}
    config: Config = None
    def get_current_language(self):
        """
        根据系统设置获取语言
        """
        system_locale = getdefaultlocale()[0]
        return system_locale

    def __init__(self, config: Config):
        self.config = config
        system_locale = self.get_current_language()
        if system_locale is not None and system_locale not in langs:
            langs = [system_locale,] + langs
        for lang in langs:
            try:
                self.load_language(lang)
                break
            except FileNotFoundError:
                pass
        if self.language_file is None:
            raise FileNotFoundError("No language file found")

    def get_string(self, key_: str, **kwarg) -> str:
        """
        获取格式化后的翻译
        """
        return self.translation_table[key_].format(**kwarg)

    def load_language(self, lang: str) -> None:
        """
        加载语言，可以丢出 FileNotFoundError 表示文件不存在
        """
        self.language_file = AssetsManager.get_assets("translations", lang + ".json")
        self.translation_table = {}
        with open(self.language_file, "r", encoding="utf-8") as f:
            self.translation_table = json.load(f)
