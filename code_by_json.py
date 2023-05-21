import json
import os
from app.ConfigManager import Config
from app.i18n import i18n
from app.HistoryBackup import HistoryBackup as HB
from app.Log import Log

filename = "code_by_json_config.json"
if not os.path.exists(filename):
    raise FileNotFoundError(f"Config file {filename} not found!")
try:
    config_json = json.load(open(filename, encoding="utf-8"))
except json.decoder.JSONDecodeError as e:
    raise ValueError(f"Config file {filename} is not a valid json file!\n{e}")
config = Config().by_dict(config_json)
i18n().__init__(config)
Log().set_default_level(config.get("LogLevel"))
HB(config).run()
