from app.Config.ConfigManager import Config
from app.i18n import i18n
from app.HistoryBackup import HistoryBackup as HB
from app.Log import log_instance

config_json = {
    "ImportPath": ".",
    "QqNumber": "1",
    "Importer": "EmptyImporter",
    "Exporter": "EmptyExporter",
}

config = Config().by_dict(config_json)
config.verify()
i18n().__init__(config)
log_instance.set_default_level(config.get("LogLevel"))
HB(config).run()
