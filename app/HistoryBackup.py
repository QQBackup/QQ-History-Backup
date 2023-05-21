from app.ConfigManager import Config


class HistoryBackup:
    def __init__(self, config: Config | None = None):
        if config is not None:
            self.set_config(config)
        self.set_config(Config())

    def set_config(self, config: Config):
        self.config = config

    def get_config(self) -> Config:
        return self.config

    def update_config(self, config: Config):
        self.config.update(config)

    def run(self):
        pass
