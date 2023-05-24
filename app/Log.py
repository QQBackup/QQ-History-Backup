import os
import sys
import logging
from time import strftime
from typing import Union
# 日志文件完整路径
FILENAME = 'log.txt'
# 设置日志格式和时间格式
FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'

class SingleLevelFilter(logging.Filter): # https://stackoverflow.com/a/1383365
    def __init__(self, passlevel: int, reject: bool):
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record) -> bool:
        if self.reject:
            return (record.levelno != self.passlevel)
        else:
            return (record.levelno == self.passlevel)

class Log: # https://zhuanlan.zhihu.com/p/166671955
    def __init__(self):
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter(fmt=FMT, datefmt=DATEFMT)
        self.log_filename = FILENAME

        self.logger.addHandler(self.get_file_handler(self.log_filename))
        self.logger.addHandler(self.get_stdout_handler())
        self.logger.addHandler(self.get_stderr_handler())
        # 设置日志的默认级别
        self.logger.setLevel(logging.INFO)

    # 输出到文件handler的函数定义
    def get_file_handler(self, filename) -> logging.FileHandler:
        filehandler = logging.FileHandler(filename, encoding="utf-8")
        filehandler.setFormatter(self.formatter)
        return filehandler

    # 输出到stdout handler的函数定义
    def get_stdout_handler(self) -> logging.StreamHandler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        f1 = SingleLevelFilter(logging.INFO, False)
        console_handler.addFilter(f1)
        return console_handler

    # 输出到stderr handler的函数定义
    def get_stderr_handler(self) -> logging.StreamHandler:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(self.formatter)
        f1 = SingleLevelFilter(logging.INFO, True)
        console_handler.addFilter(f1)
        return console_handler

    def set_default_level(self, level: Union[int, str]) -> None:
        self.logger.setLevel(level)


