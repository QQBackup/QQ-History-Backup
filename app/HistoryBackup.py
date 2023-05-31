from typing import Optional
from app.Config.ConfigManager import Config
from app.Log import log


class HistoryBackup:
    def __init__(self, config: Optional[Config] = None) -> None:
        if config is not None:
            self.set_config(config)
        self.set_config(Config())

    def set_config(self, config: Config) -> 'HistoryBackup':
        self.config: Config = config
        return self

    def get_config(self) -> Config:
        return self.config

    def update_config(self, config: Config) -> 'HistoryBackup':
        self.config.update(config)
        return self

    def run(self):
        log.info("HistoryBackup: 开始运行")
        log.info("HistoryBackup: 配置: " + str(self.config))
        pass
