# Project constants

PROJECT_NAME: str = "QQ-History-Backup"
PROJECT_AUTHOR: str = "LY"
PROJECT_URL: str = "https://github.com/Young-Lord/QQ-History-Backup"
_VERSION: tuple = (3, 0, 0)
PATH_BAN_CHARS: str = "\\  /  :  *  ?  \"  '  <  >  |  $  \r  \n".replace(
        ' ', '')
PATH_BAN_STRIPS: str = "#/~"

VERSION = "v" + '.'.join([str(i) for i in _VERSION])

# Translation constants

class TranslationNotFoundError(FileNotFoundError):
    pass

class TranslationError(ValueError):
    pass

# Config constants

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class _UNSET(Singleton):
    pass
UNSET = _UNSET()

class _NOT_PROVIDED(Singleton):
    pass
NOT_PROVIDED = _NOT_PROVIDED()

CONFIG_NECESSARY_NEVER = None
CONFIG_NECESSARY_ALWAYS = -1
CONFIG_NECESSARY_GROUPS_EXPORT_ALL = 1

class ConfigNecessaryError(ValueError):
    def __init__(self, config):
        self.message = f"ConfigNecessaryError: {config.pretty_name} (necessary value {config.necessary_group}) got {config.value}."

    def __str__(self) -> str:
        return self.message


class ConfigError(ValueError):
    def __init__(self, config, value):
        self.message = f"ConfigError: {config.pretty_name} got {value}."

    def __str__(self) -> str:
        return self.message


class OptionConfigKeyError(ConfigError):
    def __init__(self, config, value):
        self.message = f"OptionConfigKeyError: {config.pretty_name} got {value}, but expected one of {config.match_table.keys()}."


class OptionConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"OptionConfigError: {config.pretty_name} got {value}, but expected one of {config.match_table.values()}."


class ListConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"ListConfigError: {config.pretty_name} got {value}, but expected contained in {config.match_list}."

class FileConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"FileConfigError: {config.pretty_name} got {value}, but expected a valid file path."

class FolderConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"FolderConfigError: {config.pretty_name} got {value}, but expected a valid folder path."

class BoolConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"BoolConfigError: {config.pretty_name} got {value}, but expected a bool value."
