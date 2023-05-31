# Project constants

from tempfile import NamedTemporaryFile


PROJECT_NAME: str = "QQ-History-Backup"
PROJECT_AUTHOR: str = "LY"
PROJECT_URL: str = "https://github.com/Young-Lord/QQ-History-Backup"
_VERSION: tuple = (3, 0, 0)
PATH_BAN_CHARS: str = "\\  /  :  *  ?  \"  '  <  >  |  $  \r  \n".replace(" ", "")
PATH_BAN_STRIPS: str = "#/~"

VERSION = "v" + ".".join([str(i) for i in _VERSION])

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


class OptionConfigError(ConfigError):
    def __init__(self, config, value):
        self.message = f"OptionConfigError: {config.pretty_name} got {value}, but expected one of {config.match_table.keys()}."


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


# decrypt constants

_crc64_init = False
_crc64_table = [0] * 256


def crc64(s):
    global _crc64_init
    if not _crc64_init:
        for i in range(256):
            bf = i
            for j in range(8):
                if bf & 1 != 0:
                    bf = bf >> 1 ^ -7661587058870466123
                else:
                    bf >>= 1
            _crc64_table[i] = bf
        _crc64_init = True
    v = -1
    for i in range(len(s)):
        v = _crc64_table[(ord(s[i]) ^ v) & 255] ^ v >> 8
    return v


# file utils


def tempFilename() -> str:
    f = NamedTemporaryFile(delete=False)
    f.close()
    return f.name


def getSafePath(ans: str) -> str:
    """
    移除文件名中的非法字符
    """
    while True:
        ans_bak = ans
        for i in PATH_BAN_CHARS:
            ans = ans.replace(i, "")
        for i in PATH_BAN_STRIPS:
            ans = ans.strip(i)
        if ans == ans_bak:
            break
    return ans
