import os
import json
from datetime import datetime
from typing import Any


class FileManager:

    HISTORY_DATE_FORMAT = "%Y%m%d_%H%M%S"

    def __init__(self, base: str | None = None) -> None:
        self.base = base if base else ""
        self._resources_dir = os.path.join(self.base, "resources")
        self._log_dir = os.path.join(self.base, "logs")
        self._data_dir = os.path.join(self.base, "data")
        self._settings_dir = os.path.join(self._data_dir, "settings")
        self._history_dir = os.path.join(self._data_dir, "history")

        self.ensure_required_dirs()

        # key = self.generate_key()
        # self.cryptography = AESEncryptionFernet(key)

    @property
    def resources_dir(self):
        return self._resources_dir

    @property
    def log_dir(self):
        return self._log_dir

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def settings_dir(self):
        return self._settings_dir

    @property
    def history_dir(self):
        return self._history_dir

    def write_to_json(self, filepath: str, data: dict[str, Any]):
        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def read_from_json(self, filepath: str) -> Any:
        with open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)

        return data

    def write_to_str(self, filepath: str, data: str, encoding: str = "utf-8"):
        with open(filepath, "w", encoding=encoding) as f:
            f.write(data)

    def read_from_str(self, filepath: str, encoding: str = "utf-8") -> str:
        with open(filepath, "r", encoding=encoding) as f:
            data = f.read()

        return data

    def write_to_data(self, filepath: str, data: bytes):
        with open(filepath, "wb") as f:
            f.write(data)

    def read_from_data(self, filepath: str) -> bytes:
        with open(filepath, "rb") as f:
            data = f.read()

        return data

    def ensure_required_dirs(self):
        paths = [self.log_dir, self._data_dir, self.history_dir, self.settings_dir]
        for path in paths:
            if not os.path.isdir(path):
                os.makedirs(path, exist_ok=True)

    def check_required_files(self) -> dict[str, bool]:
        paths = [
            self.get_base_rules_path(),
            self.get_field_rules_path(),
            self.get_characters_path()
        ]
        result: dict[str, bool] = {}
        for path in paths:
            result[path] = os.path.isfile(path)
        return result

    # Resources
    def get_base_rules_path(self):
        file_name = f"base_rules.json"
        full_path = os.path.join(self.resources_dir, "rules", file_name)
        return full_path

    def get_field_rules_path(self):
        file_name = f"field_rules.json"
        full_path = os.path.join(self.resources_dir, "rules", file_name)
        return full_path

    def get_characters_path(self):
        file_name = f"characters.txt"
        full_path = os.path.join(self.resources_dir, file_name)
        return full_path

    # Logs
    def get_log_path(self):
        file_name = f"app.log"
        full_path = os.path.join(self.log_dir, file_name)
        return full_path

    # Settings
    def get_settings_path(self):
        file_name = f"settings.json"
        full_path = os.path.join(self.settings_dir, file_name)
        return full_path

    # History
    def get_history_path(self, date: datetime):
        name = date.strftime(self.HISTORY_DATE_FORMAT)
        file_name = f"{name}.json"
        full_path = os.path.join(self.history_dir, file_name)
        return full_path

    def list_all_history_paths(self) -> list[tuple[str, datetime]]:
        """List all history's path.

        Returns
        -------
        list[tuple[str, datetime]]
            List all history's path is descent order.
        """
        history_paths: list[tuple[str, datetime]] = []

        files = os.listdir(self.history_dir)
        files.sort(reverse=True)
        for file_name in files:
            full_path = os.path.join(self.history_dir, file_name)

            # 忽略特定檔案名稱及格式
            if not file_name.endswith(".json"):
                continue
            if not os.path.isfile(full_path):
                continue

            # 分離檔案名稱及副檔名
            name, ext = os.path.splitext(file_name)
            try:
                date = datetime.strptime(name, self.HISTORY_DATE_FORMAT)
                history_paths.append((full_path, date))
            except Exception as e:
                print(e, "This file can't not be read!")

        return history_paths

    # Key
    def get_key_path(self):
        file_name = f"key.key"
        full_path = os.path.join(self._data_dir, file_name)
        return full_path
