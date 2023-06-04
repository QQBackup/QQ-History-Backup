import sys
import logging
from typing import Union
# 日志文件完整路径
FILENAME = 'log.txt'
# 设置日志格式和时间格式
FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'
FMT_CLI = "%(asctime)s %(levelname)s: %(message)s"
DATEFMT_CLI = '%H:%M:%S'

class SingleLevelFilter(logging.Filter): # https://stackoverflow.com/a/1383365
    """
    控制只显示或不显示某个级别的日志
    """
    def __init__(self, passlevel: int, reject: bool):
        super().__init__()
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record) -> bool:
        if self.reject:
            return (record.levelno != self.passlevel)
        else:
            return (record.levelno == self.passlevel)

class Log: # https://zhuanlan.zhihu.com/p/166671955
    """
    使用 logging 模块记录日志
    """
    def __init__(self):
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter(fmt=FMT, datefmt=DATEFMT)
        self.formatter_cli = logging.Formatter(fmt=FMT_CLI, datefmt=DATEFMT_CLI)
        self.log_filename = FILENAME

        self.logger.addHandler(self.get_file_handler(self.log_filename))
        self.logger.addHandler(self.get_stdout_handler())
        self.logger.addHandler(self.get_stderr_handler())
        # 设置日志的默认级别
        self.logger.setLevel(logging.INFO)

    def get_file_handler(self, filename) -> logging.FileHandler:
        """输出到文件handler的函数定义"""
        filehandler = logging.FileHandler(filename, encoding="utf-8")
        filehandler.setFormatter(self.formatter)
        return filehandler

    def get_stdout_handler(self) -> logging.StreamHandler:
        """输出到stdout handler的函数定义"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter_cli)
        f1 = SingleLevelFilter(logging.INFO, False)
        console_handler.addFilter(f1)
        return console_handler

    def get_stderr_handler(self) -> logging.StreamHandler:
        """输出到stderr handler的函数定义"""
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(self.formatter_cli)
        f1 = SingleLevelFilter(logging.INFO, True)
        console_handler.addFilter(f1)
        return console_handler

    def set_default_level(self, level: Union[int, str]) -> None:
        """
        设置日志显示级别
        """
        self.logger.setLevel(level)

log_instance = Log()
log = log_instance.logger
