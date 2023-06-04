from locale import getlocale
import json
from typing import List, Union, Dict
from app.AssetsManager import AssetsManager
from app.Const import TranslationNotFoundError, TranslationError
from app.Log import log
from app.Const import Singleton

TRANSLATION_PATH = "translations"


class Translation:
    """
    单个翻译文件
    """

    def __init__(self, lang: str, translation_file: str):
        self.lang = lang
        self.translation_file = translation_file
        self.translation: Dict[str, str] = {}
        try:
            with open(translation_file, "r", encoding="utf-8") as f:
                self.translation = json.load(f)
        except json.decoder.JSONDecodeError as exc:
            raise TranslationError(
                "Translation file " + translation_file + " is not a valid JSON file."
            ) from exc

    def is_locale_match(self, locale: str) -> bool:
        """
        判断是否匹配某个特定语言
        """
        return self.lang == locale or self.translation.get("#WINDOWS-LOCALE") == locale


class i18n(Singleton):
    """
    翻译管理器
    """

    translations: List[Translation] = []  # 所有可用的语言列表
    languages: List[str] = []  # 正在使用的语言列表，越靠后表示越优先选择
    translation_table: Dict[str, str] = {}
    config = None

    def get_current_language(self) -> Union[str, None]:
        """
        根据系统设置获取语言
        """
        system_locale = getlocale()[0]  # 这货返回什么东西都不一定
        return system_locale

    def list_all_translations(self) -> List[Translation]:
        """
        列出所有可用的 Translation
        """
        return self.translations

    def __init__(self, config=None):
        self.config = config
        self.translations = []
        self.translation_table = {}
        self.init_all_translations()
        system_locale = self.get_current_language()
        system_locale_list = []
        if system_locale is not None:
            system_locale_list = [
                system_locale,
            ]
        langs1 = (self.config.get("LanguageFallback") if config else []) + system_locale_list + (self.config.get("LanguageCustom") if config else [])  # type: ignore
        langs_no_duplicate = []
        for lang in langs1:
            if lang not in langs_no_duplicate:
                langs_no_duplicate.append(lang)
        for lang in langs_no_duplicate:
            try:
                self.load_language(lang)
            except TranslationNotFoundError:
                pass
        if not self.languages:
            raise TranslationNotFoundError(
                "No language file found. Tried languages: " + str(langs_no_duplicate)
            )

    def get_string(self, key_: str, **kwargs) -> str:
        """
        获取格式化后的翻译
        """
        if key_ not in self.translation_table:
            log.warning("Translation key " + key_ + " not found.")
            return "[Translation key " + key_.__repr__() + " not found.]"
        return self.translation_table[key_].format(**kwargs)

    def get_all_available_languages(self) -> List[str]:
        """
        获取所有可用的语言
        """
        return [
            i.removesuffix(".json") for i in AssetsManager.list_assets(TRANSLATION_PATH)
        ]

    def init_all_translations(self) -> None:
        """
        初始化所有可用的语言
        """
        for i in self.get_all_available_languages():
            self.translations.append(
                Translation(i, AssetsManager.get_assets(TRANSLATION_PATH, i + ".json"))
            )

    def load_language(self, lang: str, override: bool = True) -> None:
        """

        加载语言，可以丢出 TranslationNotFoundError 表示文件不存在
        :param lang: 语言代码
        :param override: 是否覆盖已有的翻译，如果为 False 则会覆盖已有的翻译
        """
        matched_lang = [i for i in self.translations if i.is_locale_match(lang)]
        if len(matched_lang) == 0:
            raise TranslationNotFoundError(
                "Translation for language " + lang + " not found."
            )
        if len(matched_lang) > 1:
            raise TranslationError(
                "Multiple translations for language " + lang + " found."
            )
        json_content = matched_lang[0].translation
        if override:
            self.translation_table.update(json_content)
            self.languages.append(lang)
        else:
            old_table = self.translation_table
            self.translation_table = json_content
            self.translation_table.update(old_table)
            self.languages.insert(0, lang)

    def t(self, key_: str, **kwargs) -> str:
        """
        get_string 的简写
        """
        return self.get_string(key_, **kwargs)


t = i18n().get_string
