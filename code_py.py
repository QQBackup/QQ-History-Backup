from app.ConfigManager import Config
from app.i18n import i18n
from app.HistoryBackup import HistoryBackup as HB
from app.Log import Log

config_json = {

}

config = Config().by_dict(config_json)
i18n().__init__(config)
Log().set_default_level(config.get("LogLevel"))
HB(config).run()
