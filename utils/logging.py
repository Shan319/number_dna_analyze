# utils/logging.py
"""
數字DNA分析器 - 日誌工具
應用程式統一的日誌記錄機制

功能：
1. 設定全域日誌配置
2. 提供模組級別的日誌記錄器創建
3. 管理日誌輸出格式和目標
4. 支援不同級別的日誌記錄
5. 整合控制台和文件輸出
"""

import logging
import os
import sys
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class LoggerManager:
    """日誌管理類，負責創建和配置日誌記錄器"""

    # 單例模式，確保全域只有一個實例
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, log_dir=None, log_level=logging.INFO, enable_console=True):
        """
        初始化日誌管理器

        Args:
            log_dir (str): 日誌文件存儲目錄
            log_level (int): 日誌記錄級別
            enable_console (bool): 是否啟用控制台輸出
        """
        # 避免重複初始化
        if self.initialized:
            return

        # 設定日誌目錄
        self.log_dir = log_dir
        if self.log_dir is None:
            base_dir = Path(__file__).parent.parent
            self.log_dir = os.path.join(base_dir, "logs")

        # 確保日誌目錄存在
        os.makedirs(self.log_dir, exist_ok=True)

        # 日誌級別
        self.log_level = log_level

        # 控制台輸出設定
        self.enable_console = enable_console

        # 設定根日誌記錄器
        self._setup_root_logger()

        # 標記初始化完成
        self.initialized = True

        # 創建主應用程式日誌記錄器
        self.app_logger = self.get_logger("數字DNA分析器")
        self.app_logger.info("日誌系統初始化完成")

    def _setup_root_logger(self):
        """設定根日誌記錄器"""
        # 獲取根記錄器
        root_logger = logging.getLogger()

        # 設定全域日誌級別
        root_logger.setLevel(self.log_level)

        # 清除已有處理程序
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 創建控制台處理程序
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # 創建基本文件處理程序
        log_file = os.path.join(self.log_dir, "app.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] (%(name)s) %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # 創建每日日誌處理程序
        daily_log_file = os.path.join(self.log_dir, "daily.log")
        daily_handler = TimedRotatingFileHandler(
            daily_log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setLevel(self.log_level)
        daily_handler.setFormatter(file_formatter)
        root_logger.addHandler(daily_handler)

        # 創建錯誤日誌處理程序
        error_log_file = os.path.join(self.log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] (%(name)s) %(message)s\n'
            'File "%(pathname)s", line %(lineno)d\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)

    def get_logger(self, name):
        """
        獲取指定名稱的日誌記錄器

        Args:
            name (str): 日誌記錄器名稱，通常為模組名稱

        Returns:
            Logger: 日誌記錄器實例
        """
        return logging.getLogger(name)

    def set_level(self, level):
        """
        設定全域日誌級別

        Args:
            level (int): 日誌級別，如logging.DEBUG, logging.INFO等
        """
        self.log_level = level
        logging.getLogger().setLevel(level)

        # 更新所有處理程序的級別
        for handler in logging.getLogger().handlers:
            if not isinstance(handler, logging.handlers.RotatingFileHandler) or handler.baseFilename.endswith("error.log"):
                handler.setLevel(level)

        self.app_logger.info(f"全域日誌級別已設定為: {logging.getLevelName(level)}")

# 便捷函數

def initialize(log_dir=None, log_level=logging.INFO, enable_console=True):
    """
    初始化日誌系統

    Args:
        log_dir (str): 日誌文件存儲目錄
        log_level (int): 日誌記錄級別
        enable_console (bool): 是否啟用控制台輸出

    Returns:
        LoggerManager: 日誌管理器實例
    """
    return LoggerManager(log_dir, log_level, enable_console)

def get_logger(name):
    """
    獲取指定名稱的日誌記錄器

    Args:
        name (str): 日誌記錄器名稱，通常為模組名稱

    Returns:
        Logger: 日誌記錄器實例
    """
    # 確保管理器已初始化
    if LoggerManager._instance is None:
        initialize()

    return LoggerManager().get_logger(name)

def set_level(level):
    """
    設定全域日誌級別

    Args:
        level (int): 日誌級別，如logging.DEBUG, logging.INFO等
    """
    # 確保管理器已初始化
    if LoggerManager._instance is None:
        initialize()

    LoggerManager().set_level(level)

# 日誌級別常量 (便於導入)
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# 自定義日誌裝飾器
def log_function_call(logger=None):
    """
    函數調用日誌裝飾器

    Args:
        logger: 日誌記錄器，如果為None則使用函數所在模組的記錄器

    用法:
        @log_function_call()
        def some_function(arg1, arg2):
            pass
    """
    def decorator(func):
        # 如果沒有提供記錄器，使用函數所在模組的記錄器
        nonlocal logger
        if logger is None:
            module_name = func.__module__
            logger = get_logger(module_name)

        def wrapper(*args, **kwargs):
            logger.debug(f"調用 {func.__name__}({args}, {kwargs})")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                logger.debug(f"{func.__name__} 執行完成，耗時: {end_time - start_time:.4f}秒")
                return result
            except Exception as e:
                end_time = time.time()
                logger.error(f"{func.__name__} 執行異常，耗時: {end_time - start_time:.4f}秒，錯誤: {e}", exc_info=True)
                raise

        return wrapper

    return decorator

def log_class_methods(cls=None, exclude=None):
    """
    類方法日誌裝飾器

    Args:
        cls: 要裝飾的類，如果為None則作為裝飾器使用
        exclude: 排除的方法名列表

    用法:
        @log_class_methods
        class SomeClass:
            def method1(self):
                pass
    """
    if exclude is None:
        exclude = []

    def decorate(cls):
        # 獲取類的記錄器
        logger = get_logger(cls.__module__ + "." + cls.__name__)

        # 遍歷類的所有方法
        for name, method in cls.__dict__.items():
            # 排除特殊方法和非函數屬性
            if name.startswith('__') or name in exclude or not callable(method):
                continue

            # 使用函數裝飾器
            setattr(cls, name, log_function_call(logger)(method))

        return cls

    # 直接裝飾或返回裝飾器
    if cls is not None:
        return decorate(cls)
    return decorate

# 測試代碼
if __name__ == "__main__":
    # 初始化日誌系統
    initialize(log_level=DEBUG)

    # 獲取測試記錄器
    test_logger = get_logger("測試模組")

    # 測試各級別日誌
    test_logger.debug("這是一條調試日誌")
    test_logger.info("這是一條信息日誌")
    test_logger.warning("這是一條警告日誌")
    test_logger.error("這是一條錯誤日誌")
    test_logger.critical("這是一條嚴重錯誤日誌")

    # 測試裝飾器
    @log_function_call()
    def test_function(a, b):
        return a + b

    result = test_function(1, 2)
    print(f"函數結果: {result}")

    # 測試類方法裝飾器
    @log_class_methods
    class TestClass:
        def __init__(self, name):
            self.name = name

        def greet(self):
            return f"Hello, {self.name}!"

    test_obj = TestClass("世界")
    greeting = test_obj.greet()
    print(greeting)
