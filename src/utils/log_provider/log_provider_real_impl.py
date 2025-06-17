import os
import re
import logging
from typing import Literal
from logging import handlers

from .log_provider_interface import LogProviderInterface, Level

IS_USE_COLORAMA = True
try:
    from colorama import just_fix_windows_console, Fore, Style  # type: ignore
    just_fix_windows_console()
except ImportError as e:
    IS_USE_COLORAMA = False
    os.system("cls")

    class Fore():  # type: ignore
        LIGHTBLACK_EX = "\x1b[90m"
        LIGHTYELLOW_EX = "\x1b[93m"
        RED = "\x1b[31m"
        LIGHTRED_EX = "\x1b[91m"
        RESET = "\x1b[39m"

    class Style():  # type: ignore
        BRIGHT = "\x1b[1m"
        RESET_ALL = "\x1b[0m"


# Reference
# [1] https://www.itread01.com/content/1563349863.html
# [2] https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format
# [3] https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# [4] https://stackoverflow.com/questions/11820338/replace-default-handler-of-python-logger
# [5] https://www.codenong.com/641420/
# [6] https://stackoverflow.com/questions/338450/timedrotatingfilehandler-changing-file-name
#     * 用 suffix 給他在舊檔案後面加上日期 "%Y_%m%d" (原檔名 `<path/name.log>`，
#       加上 suffix 變成 `<path/name.log.YYYY_mmDD.log>`)
#       此時 backupCount 會失效。可用 extMatch 讓他在找檔案數量時連同這些有加 suffix 的一起尋找，確保 backupCount 正常
#     * 若希望將舊檔名改成 `<path/name.YYYY_mmDD.log>` 可用 namer 修改檔案命名方式。但此時上面的 extMatch 又失效。目前不知解法。
# [7] https://pypi.org/project/colorama/

FORMAT = "%(asctime)s.%(msecs)03d <%(name)s(%(process)d)> [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class FileFormatter(logging.Formatter):
    """File log formatter"""
    ...


class ConsoleFormatter(logging.Formatter):
    """Console color log formatter

    Want to coloring the log with different level. See [3], [7]
    """

    def __init__(self,
                 fmt: str | None = None,
                 datefmt: str | None = None,
                 style: Literal['%', '{', '$'] = "%",
                 validate: bool = True,
                 *,
                 defaults=None) -> None:

        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

        if fmt is None:
            fmt = self._style._fmt

        # Prepare colored formats for different levels
        colored_format = {
            logging.DEBUG: Fore.LIGHTBLACK_EX + fmt + Fore.RESET,
            logging.INFO: fmt,
            logging.WARNING: Fore.LIGHTYELLOW_EX + fmt + Fore.RESET,
            logging.ERROR: Fore.RED + fmt + Fore.RESET,
            logging.CRITICAL: Fore.LIGHTRED_EX + Style.BRIGHT + fmt + Fore.RESET + Style.RESET_ALL
        }
        self.colored_formatter = {
            levelno: FileFormatter(log_fmt, self.datefmt, style, validate, defaults=defaults)
            for levelno, log_fmt in colored_format.items()
        }

    # overwrite
    def format(self, record):
        """Logging Formatter to add colors and count warning / errors"""
        formatter = self.colored_formatter.get(record.levelno)
        return formatter.format(record) if formatter else super().format(record)


class LogProviderRealImpl(LogProviderInterface):
    """
    Global root logger based log provider

    All loggers inherit settings from the root logger, including third-party library loggers.
    This allows unified control of logging behavior for the entire application.
    """

    # Class-level flag to ensure initialization only happens once
    _root_configured: bool = False

    def __init__(self,
                 log_base_dir: str,
                 project: str | None,
                 service: str,
                 wants_file_handler: bool = True,
                 wants_cmd_handler: bool = True) -> None:
        super().__init__()

        self.log_base_dir = log_base_dir
        self.project = project
        self.service = service
        self.wants_file_handler = wants_file_handler
        self.wants_cmd_handler = wants_cmd_handler

        # Ensure log directory exists
        if project:
            self.log_file_dir = os.path.join(log_base_dir, project)
        else:
            self.log_file_dir = log_base_dir
        self._ensure_log_directory(self.log_file_dir)

        # Configure global root logger (only once)
        if not LogProviderRealImpl._root_configured:
            self._config_root_logger()
            LogProviderRealImpl._root_configured = True

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """Get a logger instance

        Parameters
        ----------
        name : str | None, optional
            Logger name. If None, uses service name.

        Returns
        -------
        logging.Logger
            Logger instance that automatically inherits root logger settings
        """
        if name is None:
            name = self.service
        if name.startswith(self.service):
            logger = logging.getLogger(name)
        else:
            logger = logging.getLogger(self.service).getChild(name)

        # Ensure all loggers propagate to root logger
        # This way root logger's handlers and level settings affect all loggers
        logger.propagate = True

        return logger

    def _ensure_log_directory(self, directory: str) -> str:
        """Ensure log directory exists"""
        os.makedirs(directory, exist_ok=True)
        return directory

    def _config_root_logger(self):
        """
        Configure root logger

        This is the core configuration of the entire logging system.
        All other loggers will inherit these settings.
        """
        # Get the actual root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)

        # Clear existing handlers to avoid duplication
        root_logger.handlers.clear()

        # Create formatters
        file_formatter = FileFormatter(FORMAT, DATE_FORMAT)
        console_formatter = ConsoleFormatter(FORMAT, DATE_FORMAT)

        # Add file handler
        if self.wants_file_handler:
            file_handler = self._create_file_handler(file_formatter)
            root_logger.addHandler(file_handler)

        # Add console handler
        if self.wants_cmd_handler:
            cmd_handler = self._create_console_handler(console_formatter)
            root_logger.addHandler(cmd_handler)

        # Ensure root logger doesn't propagate upward (it's already at the top)
        root_logger.propagate = False

    def _create_file_handler(self, formatter: logging.Formatter) -> logging.Handler:
        """Create file handler"""
        file_name = os.path.join(self.log_file_dir, f"{self.service}.log")
        file_handler = handlers.TimedRotatingFileHandler(file_name,
                                                         when="midnight",
                                                         interval=1,
                                                         backupCount=30,
                                                         encoding="utf-8")
        file_handler.suffix = "%Y_%m%d.log"
        file_handler.extMatch = re.compile(r"^\d{4}_\d{4}\.log$")
        file_handler.setFormatter(formatter)
        return file_handler

    def _create_console_handler(self, formatter: logging.Formatter) -> logging.Handler:
        """Create console handler"""
        cmd_handler = logging.StreamHandler()
        cmd_handler.setFormatter(formatter)
        return cmd_handler

    def set_level(self, level: int | str | Level):
        """Set global log level

        This affects all loggers, including third-party library loggers

        Parameters
        ----------
        level : int | str | Level
            Log level (logging.INFO, "INFO", Level.INFO, etc.)
        """
        if isinstance(level, str):
            level = Level[level]

        # Set app logger level
        app_level_logger = self.get_logger()
        app_level_logger.setLevel(level)

        # Also set level for all handlers
        for handler in app_level_logger.handlers:
            handler.setLevel(level)

    def set_global_level(self, level: int | str | Level):
        """Set global log level including third-party libraries

        This method affects ALL loggers including third-party ones.
        Use this if you want the old behavior.

        Parameters
        ----------
        level : int | str | Level
            Log level (logging.INFO, "INFO", Level.INFO, etc.)
        """
        if isinstance(level, str):
            level = Level[level]

        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Also set level for all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level)

        # Set level for all existing loggers
        for _, logger in logging.Logger.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                logger.setLevel(level)

    def set_library_level(self, library_name: str, level: int | str | Level):
        """Set log level for a specific library

        This is useful for controlling third-party library log output
        Example: set_library_level('matplotlib', logging.WARNING)

        Parameters
        ----------
        library_name : str
            Library name
        level : int | str | Level
            Log level (logging.INFO, "INFO", Level.INFO, etc.)
        """
        if isinstance(level, str):
            level = Level[level]

        library_logger = logging.getLogger(library_name)
        library_logger.setLevel(level)

    def silence_library(self, library_name: str):
        """Silence log output from a specific library

        Parameters
        ----------
        library_name : str
            Library name to silence
        """
        self.set_library_level(library_name, logging.CRITICAL + 1)

    # Convenient logging methods
    def log(self,
            level: int | str | Level,
            msg: object,
            logger_name: str | None = None,
            *args,
            **kwargs):
        if isinstance(level, str):
            level = Level[level]

        logger = self.get_logger(logger_name)
        logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        logger = self.get_logger(logger_name)
        logger.debug(msg, *args, **kwargs)

    def info(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        logger = self.get_logger(logger_name)
        logger.info(msg, *args, **kwargs)

    def warning(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        logger = self.get_logger(logger_name)
        logger.warning(msg, *args, **kwargs)

    def error(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        logger = self.get_logger(logger_name)
        logger.error(msg, *args, **kwargs)

    def critical(self, msg: object, logger_name: str | None = None, *args, **kwargs):
        logger = self.get_logger(logger_name)
        logger.critical(msg, *args, **kwargs)

    def get_all_loggers(self) -> dict[str, logging.Logger]:
        """Get all existing loggers

        Returns
        -------
        dict[str, logging.Logger]
            Dictionary of all loggers
        """
        return {
            name: logger
            for name, logger in logging.Logger.manager.loggerDict.items()
            if isinstance(logger, logging.Logger)
        }

    def list_logger_names(self) -> list[str]:
        """List all logger names

        Returns
        -------
        list[str]
            List of logger names
        """
        return list(logging.Logger.manager.loggerDict.keys())

    def reset_logging_config(self):
        """Reset logging configuration

        Note: This will clear all logger configurations. Use with caution.
        """
        # 清除所有處理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        # 重置類級別標誌
        LogProviderRealImpl._root_configured = False

        # 重新配置
        self._config_root_logger()
        LogProviderRealImpl._root_configured = True

    @classmethod
    def reset_class_state(cls):
        """Reset class state"""
        cls._root_configured = False
