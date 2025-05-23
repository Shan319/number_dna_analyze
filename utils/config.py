# utils/config.py
"""
設定檔
管理處理應用程式所有設定

負責載入、儲存和管理應用程式的設定參數，
確保各功能能夠存取統一的控制信息。
"""
import os
import json
import logging
from pathlib import Path

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.Config")

# 默認設定
DEFAULT_CONFIG = {
    "app_name": "數字DNA分析器",
    "version": "1.0.0",
    "rules_dir": "resources/rules",
    "base_rules_file": "base_rules.json",
    "field_rules_file": "field_rules.json",
    "logs_dir": "logs",
    "data_dir": "data",
    "ui": {
        "width": 1000,
        "height": 600,
        "theme": "light"
    },
    "analysis": {
        "max_recommendations": 3,  # 最大推薦數量
        "max_candidates": 1000,  # 最大候選數字數量
        "calculation_timeout": 5  # 計算超時時間(秒)
    },
    "data": {
        "use_encryption": True,  # 是否使用加密
        "history_dir": "data/history",  # 歷史記錄目錄
        "max_history_items": 50  # 最大歷史記錄數量
    },
    "features": {
        "encryption": True,
        "advanced_analysis": True,
        "report_generation": True
    }
}

# 全域設定
_config = None


def initialize(config_file=None):
    """
    初始化配置管理器

    Args:
        config_file: 設定文件路徑，若未提供則使用默認路徑

    Returns:
        配置管理器實例
    """
    global _config

    # 如果已經初始化，直接返回
    if _config is not None:
        return _config

    # 創建新的設定實例
    _config = Config(config_file)
    logger.info("配置管理器已初始化")

    return _config


def get_config(key=None, default=None):
    """
    獲取設定值

    Args:
        key: 設定鍵，可以使用點號分隔的路徑，如 "ui.theme"
        default: 如果設定不存在，返回的默認值

    Returns:
        設定值或默認值
    """
    global _config

    # 確保配置已初始化
    if _config is None:
        initialize()

    # 如果沒有提供鍵名，返回整個配置
    if key is None:
        return _config.config

    return _config.get(key, default)


def set_config(key, value):
    """
    設置設定值

    Args:
        key: 設定鍵，可以使用點號分隔的路徑，如 "ui.theme"
        value: 要設置的值

    Returns:
        成功設置返回True，否則返回False
    """
    global _config

    # 確保配置已初始化
    if _config is None:
        initialize()

    try:
        _config.set(key, value)
        return True
    except Exception as e:
        logger.error(f"設置配置失敗: {e}")
        return False


def save_config(config_file=None):
    """
    保存設定到文件

    Args:
        config_file: 設定文件路徑，若未提供則使用當前路徑

    Returns:
        成功保存返回True，否則返回False
    """
    global _config

    # 確保配置已初始化
    if _config is None:
        initialize()

    # 如果提供了新的文件路徑，更新配置文件路徑
    if config_file:
        _config.config_file = config_file

    try:
        _config.save_config()
        return True
    except Exception as e:
        logger.error(f"保存配置失敗: {e}")
        return False


def get_path(key):
    """
    獲取路徑設定

    Args:
        key: 路徑鍵名，如 "data_dir", "logs_dir"

    Returns:
        路徑字符串，如果不存在則返回None
    """
    # 直接從配置獲取路徑
    path = get_config(key)

    # 如果是路徑相關的鍵，確保目錄存在
    if path and key.endswith('_dir'):
        os.makedirs(path, exist_ok=True)

    return path


def is_feature_enabled(feature_name):
    """
    檢查特定功能是否啟用

    Args:
        feature_name: 功能名稱

    Returns:
        如果功能啟用返回True，否則返回False
    """
    return get_config(f"features.{feature_name}", False)


class Config:
    """管理設定類，處理應用程式設定"""

    def __init__(self, config_file=None):
        """
        Args:
            config_file: 設定文件路徑，若未提供則使用默認路徑
        """
        # 設定默認參數
        self.config = DEFAULT_CONFIG.copy()

        # 如果提供了設定文件，則載入
        if config_file:
            self.config_file = config_file
            self.load_config()
        else:
            # 默認設定文件路徑
            self.config_file = os.path.join("resources", "config.json")
            # 如果文件存在則載入，否則使用默認值
            if os.path.exists(self.config_file):
                self.load_config()

    def load_config(self):
        """從檔案載入設定"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # 更新設定，但保留默認值中存在而加載的設定中不存在的項
                self._update_config_recursive(self.config, loaded_config)
            logger.info(f"已載入配置: {self.config_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入設定失敗: {e}")

    def _update_config_recursive(self, target, source):
        """遞迴更新設定字典，保留原有層級結構

        Args:
            target: 目標設定字典
            source: 來源設定字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # 如果兩者都是字典，遞迴更新
                self._update_config_recursive(target[key], value)
            else:
                # 否則直接替換
                target[key] = value

    def save_config(self):
        """保存設定到文件"""
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存配置: {self.config_file}")
        except Exception as e:
            logger.error(f"保存設定失敗: {e}")
            raise

    def get(self, key, default=None):
        """獲取設定值

        Args:
            key: 設定鍵，可以使用點號分隔的路徑，如 "ui.theme"
            default: 如果設定不存在，返回的默認值

        Returns:
            設定值或默認值
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key, value):
        """設置設定值

        Args:
            key: 設定鍵，可以使用點號分隔的路徑，如 "ui.theme"
            value: 要設置的值
        """
        keys = key.split('.')
        config = self.config

        # 對於多層次鍵，遍歷到倒數第二層
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # 設置最後一層的值
        config[keys[-1]] = value

    def get_rules_path(self, rules_file):
        """獲取規則文件的完整路徑

        Args:
            rules_file: 規則文件名

        Returns:
            規則文件的完整路徑
        """
        rules_dir = self.get("rules_dir")
        return os.path.join(rules_dir, rules_file)

    def get_base_rules_path(self):
        """獲取基本規則文件的完整路徑

        Returns:
            基本規則文件的完整路徑
        """
        return self.get_rules_path(self.get("base_rules_file"))

    def get_field_rules_path(self):
        """獲取磁場規則文件的完整路徑

        Returns:
            磁場規則文件的完整路徑
        """
        return self.get_rules_path(self.get("field_rules_file"))


# 初始化全域設定
initialize()
