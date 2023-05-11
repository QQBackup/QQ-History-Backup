from app.ConfigManager import Config
class HistoryBackup:
    config: Config = None
    def set_config(self, config: Config):
        self.config = config
    def update_config(self, config: Config):
        self.config.update(config)
    def run(self):
        pass