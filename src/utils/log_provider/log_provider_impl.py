import os
import re
import logging
from typing import Literal
from logging import handlers

from .log_provider_interface import LogProviderInterface

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

LEVEL = logging.DEBUG
FORMAT = "%(asctime)s.%(msecs)03d <%(name)s(%(process)d)> [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Want to use "." rather than "," for milli-seconds. See [2]
# Now can easily fix by add .%(msecs)03d in FORMAT
class FileFormatter(logging.Formatter):
    ...


# Want to coloring the log with different level. See [3], [7]
class ConsoleFormatter(logging.Formatter):

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

        # prepare colored formatters
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
        return formatter.format(record)  # type: ignore


class LogProvideImpl(LogProviderInterface):

    def __init__(self,
                 file_name: str,
                 wants_file_handler: bool = True,
                 wants_cmd_handler: bool = True) -> None:
        super().__init__()
        self._loggers: dict[str, logging.Logger] = {}
        self._loggers["root"] = self._config_logger(file_name, wants_file_handler,
                                                    wants_cmd_handler)

    def get_logger(self, name: str = "root") -> logging.Logger:
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)
        self._loggers[name] = logger
        return logger

    def _config_logger(self,
                       file_name: str,
                       wants_file_handler: bool = True,
                       wants_cmd_handler: bool = True):
        # 將 handlers 添加到根 logger，這樣所有子 logger 都會套用一樣的設定
        root_logger = logging.getLogger()
        root_logger.setLevel(LEVEL)

        file_formatter = FileFormatter(FORMAT, DATE_FORMAT)
        console_formatter = ConsoleFormatter(FORMAT, DATE_FORMAT)

        has_file_handler: bool = False
        has_cmd_handler: bool = False
        for handler in root_logger.handlers:
            if isinstance(handler, handlers.TimedRotatingFileHandler):
                has_file_handler = True
            if isinstance(handler, logging.StreamHandler):
                has_cmd_handler = True

        if wants_file_handler and not has_file_handler:
            # Separate the log file date-by-date. See [1], [6]
            file_handler = handlers.TimedRotatingFileHandler(file_name,
                                                             when="midnight",
                                                             interval=1,
                                                             backupCount=30,
                                                             encoding="utf-8")
            file_handler.suffix = "%Y_%m%d.log"
            file_handler.extMatch = re.compile(r"^\d{4}_\d{4}$")

            file_handler.setLevel(LEVEL)
            file_handler.setFormatter(file_formatter)  # type: ignore
            root_logger.addHandler(file_handler)

        if wants_cmd_handler and not has_cmd_handler:
            cmd_handler = logging.StreamHandler()
            cmd_handler.setLevel(LEVEL)
            cmd_handler.setFormatter(console_formatter)
            root_logger.addHandler(cmd_handler)

        # If propagate is True, the logger will shows twice with logger and root itself. See [4]
        # root_logger.propagate = False

        return root_logger

    def set_level(self, level: int):
        self.get_logger("root").setLevel(level)

    def log(self, level: int, msg: object, *args, **kwargs):
        self.get_logger("root").log(level, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs):
        self.get_logger("root").debug(msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs):
        self.get_logger("root").info(msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs):
        self.get_logger("root").warning(msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs):
        self.get_logger("root").error(msg, *args, **kwargs)

    def critical(self, msg: object, *args, **kwargs):
        self.get_logger("root").critical(msg, *args, **kwargs)
