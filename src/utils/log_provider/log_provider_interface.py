from abc import ABC, abstractmethod
from enum import Enum
# 參考這個
import logging
"""
CRITICAL = 50
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
"""


# https://zamhuang.medium.com/linux-%E5%A6%82%E4%BD%95%E5%8D%80%E5%88%86-log-level-216b975649a4
class Level(Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG


class LogProviderInterface(ABC):

    @abstractmethod
    def get_logger(self, name: str = "root") -> logging.Logger:
        ...

    @abstractmethod
    def set_level(self, level: int):
        pass

    @abstractmethod
    def log(self, level, msg, *args, **kwargs):
        pass

    @abstractmethod
    def debug(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def critical(self, msg, *args, **kwargs):
        pass
