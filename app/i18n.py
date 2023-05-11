from locale import getdefaultlocale
import json
from app.AssetsManager import AssetsManager
from app.ConfigManager import Config
from app.Const import TranslationNotFoundError
class i18n():
    # singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    languages: list = None
    translation_table: dict = None
    config: Config = None

    def get_current_language(self):
        """
        根据系统设置获取语言
        """
        system_locale = getdefaultlocale()[0]
        return system_locale

    def __init__(self, config: Config = None):
        self.config = config
        self.languages = []
        self.translation_table = {}
        system_locale = self.get_current_language()
        langs1 = (self.config.language_custom if config else []) + [system_locale,] + (self.config.language_fallback if config else [])
        langs = []
        [langs.append(lang) for lang in langs1 if lang is not None and lang not in langs] # 去重
        for lang in langs:
            try:
                self.load_language(lang)
            except TranslationNotFoundError:
                pass
        if self.languages == []:
            raise TranslationNotFoundError("No language file found. Tried languages: " + str(langs))

    def get_string(self, key_: str, **kwarg) -> str:
        """
        获取格式化后的翻译
        """
        return self.translation_table[key_].format(**kwarg)

    def load_language(self, lang: str, override: bool = False) -> None:
        """
        加载语言，可以丢出 TranslationNotFoundError 表示文件不存在
        """
        try:
            lang_file = AssetsManager.get_assets("translations", lang + ".json")
        except FileNotFoundError as e:
            raise TranslationNotFoundError(e.filename)
        self.languages.append(lang)
        with open(lang_file, "r", encoding="utf-8") as f:
            if override:
                old_table = self.translation_table
                self.translation_table = json.load(f)
                self.translation_table.update(old_table)
            else:
                self.translation_table.update(json.load(f))
