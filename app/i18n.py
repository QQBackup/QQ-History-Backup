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
    languages: list = None # 语言列表，越靠后表示越后覆盖
    translation_table: dict = None
    config: Config = None

    def get_current_language(self):
        """
        根据系统设置获取语言
        """
        system_locale = getdefaultlocale()[0]
        return system_locale
    
    def list_all_languages(self) -> list:
        """
        列出所有语言
        """
        return self.languages

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

    def load_language(self, lang: str, override: bool = True) -> None:
        """
        
        加载语言，可以丢出 TranslationNotFoundError 表示文件不存在
        :param lang: 语言代码
        :param override: 是否覆盖已有的翻译，如果为 False 则会覆盖已有的翻译
        """
        try:
            lang_file = AssetsManager.get_assets("translations", lang + ".json")
        except FileNotFoundError as e:
            raise TranslationNotFoundError(e.filename)
        with open(lang_file, "r", encoding="utf-8") as f:
            if override:
                self.translation_table.update(json.load(f))
                self.languages.append(lang)
            else:
                old_table = self.translation_table
                self.translation_table = json.load(f)
                self.translation_table.update(old_table)
                self.languages.insert(0, lang)
    
    def t(self, key_: str, **kwarg) -> str:
        """
        get_string 的简写
        """
        return self.get_string(key_, **kwarg)

t = i18n().get_string