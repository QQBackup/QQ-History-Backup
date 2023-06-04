from typing import Optional
from app.Config.ConfigManager import Config
from app.Log import log
from app.i18n import t
from app.Importer.BaseImporter import BaseImporter
from app.Exporter.BaseExporter import BaseExporter


class HistoryBackup:
    importer: BaseImporter = None
    exporter: BaseExporter = None
    def __init__(self, config: Optional[Config] = None) -> None:
        if config is not None:
            self.set_config(config)
        else:
            self.set_config(Config())

    def set_config(self, config: Config) -> 'HistoryBackup':
        """
        设置配置
        :param config: 配置
        """
        self.config: Config = config
        return self

    def get_config(self) -> Config:
        """
        获取配置
        """
        return self.config

    def update_config(self, config: Config) -> 'HistoryBackup':
        """
        更新配置
        """
        self.config.update(config)
        return self

    def run(self):
        """
        运行
        """
        log.info("HistoryBackup: 开始运行")
        log.info("HistoryBackup: 配置: " + str(self.config))
        self.importer = self.config.get("Importer")(config=self.config)
#        print(self.config.get("Importer").detect_possibility_of_import(config=self.config))
        self.exporter = self.config.get("Exporter")(config=self.config)
        print(self.importer.get_friend_list())
        print(self.importer.get_group_list())
        chat_type = self.config.get("ChatType")
        if not self.config.get("ExportAll"):
            qq_number = self.config.get("QqNumber")
            if chat_type not in {"friend", "group"}:
                raise ValueError(f"ChatType: {chat_type} 不合法")
            obj = self.importer.get_friend_by_uin(qq_number) if chat_type == "friend" else self.importer.get_group_by_uin(qq_number)
            msg = self.importer.get_chat_message(obj)
            print(msg)
        else:
            if chat_type in {"friend", "all"}:
                for i in self.importer.get_friend_list():
                    msg = self.importer.get_chat_message(i)
                    print(msg)
            if chat_type in {"group", "all"}:
                for i in self.importer.get_group_list():
                    msg = self.importer.get_chat_message(i)
                    print(msg)
        log.info("HistoryBackup: 运行结束")

