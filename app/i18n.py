from locale import getdefaultlocale
import json
from app.AssetsManager import AssetsManager
from app.Const import TranslationNotFoundError, TranslationError
from app.Log import Log
log = Log().logger

TRANSLATION_PATH = "translations"
class i18n():
    # singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    languages: list = [] # 语言列表，越靠后表示越后覆盖
    translation_table: dict = {}
    config = None

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

    def __init__(self, config = None):
        self.config = config
        self.languages = []
        self.translation_table = {}
        system_locale = self.get_current_language()
        langs1 = (self.config.get("LanguageFallback") if config else []) + [system_locale,] + (self.config.get("LanguageCustom") if config else []) # type: ignore
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
    
    def get_all_available_languages(self) -> list[str]:
        """
        获取所有可用的语言
        """
        return [i.removesuffix(".json") for i in AssetsManager.list_assets(TRANSLATION_PATH)]

    def load_language(self, lang: str, override: bool = True) -> None:
        """
        
        加载语言，可以丢出 TranslationNotFoundError 表示文件不存在
        :param lang: 语言代码
        :param override: 是否覆盖已有的翻译，如果为 False 则会覆盖已有的翻译
        """
        try:
            lang_file = AssetsManager.get_assets(TRANSLATION_PATH, lang + ".json")
        except FileNotFoundError as e:
            raise TranslationNotFoundError(e.filename)
        with open(lang_file, "r", encoding="utf-8") as f:
            try:
                json_content = json.load(f)
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                raise TranslationError("Translation file " + lang_file + " is not a valid json file.")
            if override:
                self.translation_table.update(json_content)
                self.languages.append(lang)
            else:
                old_table = self.translation_table
                self.translation_table = json_content
                self.translation_table.update(old_table)
                self.languages.insert(0, lang)
    
    def t(self, key_: str, **kwarg) -> str:
        """
        get_string 的简写
        """
        return self.get_string(key_, **kwarg)

t = i18n().get_string