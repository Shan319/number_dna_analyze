"""
設定檔
管理處理應用程式所有設定

負責載入、儲存和管理應用程式的設定參數，
確保各功能能夠存取統一的控制信息。
"""
import os
import json
from pathlib import Path

class Config:
    """管理設定類，處理應用程式設定"""

    def __init__(self, config_file=None):
        """
        參數:
            config_file: 設定文件路徑，若未提供則使用默認路徑
        """
        # 設定默認參數
        self.config = {
            "app_name": "數字DNA分析器",
            "version": "1.0.0",
            "rules_dir": "resources/rules",
            "base_rules_file": "base_rules.json",
            "field_rules_file": "field_rules.json",
            "ui": {
                "width": 1000,
                "height": 600,
                "theme": "light"
            },
            "analysis": {
                "max_recommendations": 3,  # 最大推薦數量
                "max_candidates": 1000,    # 最大候選數字數量
                "calculation_timeout": 5   # 計算超時時間(秒)
            },
            "data": {
                "use_encryption": True,    # 是否使用加密
                "history_dir": "data/history",  # 歷史記錄目錄
                "max_history_items": 50    # 最大歷史記錄數量
            }
        }

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
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"載入設定失敗: {e}")

    def _update_config_recursive(self, target, source):
        """遞迴更新設定字典，保留原有層級結構

        參數:
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
        except Exception as e:
            print(f"保存設定失敗: {e}")

    def get(self, key, default=None):
        """獲取設定值

        參數:
            key: 設定鍵，可以使用點號分隔的路徑，如 "ui.theme"
            default: 如果設定不存在，返回的默認值

        返回:
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

        參數:
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

        參數:
            rules_file: 規則文件名

        返回:
            規則文件的完整路徑
        """
        rules_dir = self.get("rules_dir")
        return os.path.join(rules_dir, rules_file)

    def get_base_rules_path(self):
        """獲取基本規則文件的完整路徑

        返回:
            基本規則文件的完整路徑
        """
        return self.get_rules_path(self.get("base_rules_file"))

    def get_field_rules_path(self):
        """獲取磁場規則文件的完整路徑

        返回:
            磁場規則文件的完整路徑
        """
        return self.get_rules_path(self.get("field_rules_file"))


# 全局設定實例
config = Config()
