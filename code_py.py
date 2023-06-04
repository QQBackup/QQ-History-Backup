import os
from app.Config.ConfigManager import Config
from app.i18n import i18n
from app.HistoryBackup import HistoryBackup as HB
from app.Log import log_instance

config_json = {
    "ImportPath": "QQ-mix",
    "QqNumber": os.listdir("QQ-mix")[0].replace(".db", ""), # 也可以直接写你的 QQ 号
    "Importer": "AndroidQq",
    "Exporter": "EmptyExporter",
}

config = Config().by_dict(config_json).verify()
i18n().__init__(config)
log_instance.set_default_level(config.get("LogLevel"))
HB(config).run()
