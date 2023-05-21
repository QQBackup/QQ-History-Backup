PROJECT_NAME: str = "QQ-History-Backup"
PROJECT_AUTHOR: str = "LY"
PROJECT_URL: str = "https://github.com/Young-Lord/QQ-History-Backup"
_VERSION: tuple = (3, 0, 0)
PATH_BAN_CHARS: str = "\\  /  :  *  ?  \"  '  <  >  |  $  \r  \n".replace(
        ' ', '')
PATH_BAN_STRIPS: str = "#/~"

VERSION = "v" + '.'.join([str(i) for i in _VERSION])

class TranslationNotFoundError(FileNotFoundError):
    pass

class TranslationError(ValueError):
    pass
