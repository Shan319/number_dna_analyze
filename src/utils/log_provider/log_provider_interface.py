from abc import ABC, abstractmethod
from enum import IntEnum
import logging


# https://zamhuang.medium.com/linux-%E5%A6%82%E4%BD%95%E5%8D%80%E5%88%86-log-level-216b975649a4
class Level(IntEnum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class LogProviderInterface(ABC):

    @abstractmethod
    def get_logger(self, name: str | None = None) -> logging.Logger:
        raise NotImplementedError()

    @abstractmethod
    def set_level(self, level: int | str | Level):
        raise NotImplementedError()

    @abstractmethod
    def log(self,
            level: int | str | Level,
            msg: object,
            logger_name: str | None = None,
            *args,
            **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def debug(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def info(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def warning(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def error(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def critical(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        raise NotImplementedError()
