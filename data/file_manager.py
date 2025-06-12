# data/file_manager.py
"""
數字DNA分析器 - 檔案管理器
負責處理應用程式的檔案存取與管理

功能：
1. 管理分析結果的儲存與讀取
2. 處理歷史紀錄的存取
3. 加載應用程式資源檔案
4. 提供檔案加密與解密功能
5. 支援檔案匯入匯出功能
"""

import os
import json
import shutil
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, BinaryIO, TextIO
import datetime

# 嘗試導入加密模組 (如果可用)
try:
    from data.encryption import encrypt_data, decrypt_data, is_encrypted
    encryption_available = True
except ImportError:
    encryption_available = False

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.FileManager")


class FileManager:
    """檔案管理類，負責檔案讀寫操作"""

    def __init__(self,
                 base_dir: str | None = None,
                 history_dir: str | None = None,
                 resources_dir: str | None = None,
                 enable_encryption: bool = True):
        """檔案管理器

        Parameters
        ----------
        base_dir : str | None, optional
            應用程式基礎目錄，如果為 None 則使用預設路徑
        history_dir : str | None, optional
            歷史紀錄儲存目錄，如果為 None 則使用預設路徑
        resources_dir : str | None, optional
            資源檔案目錄，如果為 None 則使用預設路徑
        enable_encryption : bool, optional
            是否啟用加密功能，預設為 True
        """
        self.logger = logging.getLogger("數字DNA分析器.FileManager")

        # 設定基礎目錄
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)

        # 設定歷史紀錄目錄
        if history_dir is None:
            self.history_dir = self.base_dir / "data" / "history"
        else:
            self.history_dir = Path(history_dir)

        # 設定資源目錄
        if resources_dir is None:
            self.resources_dir = self.base_dir / "resources"
        else:
            self.resources_dir = Path(resources_dir)

        # 確保目錄存在
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.resources_dir, exist_ok=True)

        # 加密設定
        self.enable_encryption = enable_encryption and encryption_available
        if self.enable_encryption and not encryption_available:
            self.logger.warning("加密模組不可用，已停用加密功能")
            self.enable_encryption = False

        self.logger.info(f"檔案管理器初始化完成，基礎目錄: {self.base_dir}")
        self.logger.info(f"歷史紀錄目錄: {self.history_dir}")
        self.logger.info(f"資源目錄: {self.resources_dir}")
        self.logger.info(f"加密功能: {'啟用' if self.enable_encryption else '停用'}")

    # ------ 資源檔案管理 ------

    def get_resource_path(self, relative_path: str) -> Path:
        """
        獲取資源檔案路徑

        Args:
            relative_path (str): 相對於資源目錄的檔案路徑

        Returns:
            Path: 完整檔案路徑
        """
        return self.resources_dir / relative_path

    def load_resource_file(self, relative_path: str, encoding: str = 'utf-8') -> str:
        """
        讀取資源檔案內容

        Args:
            relative_path (str): 相對於資源目錄的檔案路徑
            encoding (str): 檔案編碼

        Returns:
            str: 檔案內容

        異常:
            FileNotFoundError: 檔案不存在時拋出
        """
        file_path = self.get_resource_path(relative_path)

        if not file_path.exists():
            self.logger.error(f"資源檔案不存在: {file_path}")
            raise FileNotFoundError(f"資源檔案不存在: {file_path}")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            self.logger.debug(f"成功讀取資源檔案: {file_path}")
            return content
        except Exception as e:
            self.logger.error(f"讀取資源檔案失敗: {file_path}, 錯誤: {e}")
            raise

    def load_resource_json(self, relative_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        讀取JSON格式的資源檔案

        Args:
            relative_path (str): 相對於資源目錄的檔案路徑
            encoding (str): 檔案編碼

        Returns:
            Dict[str, Any]: 解析後的JSON數據

        異常:
            FileNotFoundError: 檔案不存在時拋出
            json.JSONDecodeError: JSON解析錯誤時拋出
        """
        file_path = self.get_resource_path(relative_path)

        if not file_path.exists():
            self.logger.error(f"JSON資源檔案不存在: {file_path}")
            raise FileNotFoundError(f"JSON資源檔案不存在: {file_path}")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)

            self.logger.debug(f"成功讀取JSON資源檔案: {file_path}")
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析錯誤: {file_path}, 錯誤: {e}")
            raise
        except Exception as e:
            self.logger.error(f"讀取JSON資源檔案失敗: {file_path}, 錯誤: {e}")
            raise

    def save_resource_file(self,
                           relative_path: str,
                           content: str,
                           encoding: str = 'utf-8',
                           create_dirs: bool = True) -> bool:
        """
        儲存內容到資源檔案

        Args:
            relative_path (str): 相對於資源目錄的檔案路徑
            content (str): 要儲存的內容
            encoding (str): 檔案編碼
            create_dirs (bool): 是否自動創建父目錄

        Returns:
            bool: 儲存是否成功
        """
        file_path = self.get_resource_path(relative_path)

        if create_dirs:
            os.makedirs(file_path.parent, exist_ok=True)

        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)

            self.logger.debug(f"成功儲存資源檔案: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"儲存資源檔案失敗: {file_path}, 錯誤: {e}")
            return False

    def save_resource_json(self,
                           relative_path: str,
                           data: Dict[str, Any],
                           encoding: str = 'utf-8',
                           create_dirs: bool = True,
                           indent: int = 4) -> bool:
        """
        儲存數據到JSON資源檔案

        Args:
            relative_path (str): 相對於資源目錄的檔案路徑
            data (Dict[str, Any]): 要儲存的數據
            encoding (str): 檔案編碼
            create_dirs (bool): 是否自動創建父目錄
            indent (int): JSON縮排空格數

        Returns:
            bool: 儲存是否成功
        """
        file_path = self.get_resource_path(relative_path)

        if create_dirs:
            os.makedirs(file_path.parent, exist_ok=True)

        try:
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)

            self.logger.debug(f"成功儲存JSON資源檔案: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"儲存JSON資源檔案失敗: {file_path}, 錯誤: {e}")
            return False

    # ------ 歷史紀錄管理 ------

    def get_history_path(self, history_type: str) -> Path:
        """
        獲取特定類型的歷史紀錄目錄

        Args:
            history_type (str): 歷史紀錄類型，如 'name', 'id', 'analysis'

        Returns:
            Path: 歷史紀錄目錄路徑
        """
        history_subdir = self.history_dir / history_type
        os.makedirs(history_subdir, exist_ok=True)
        return history_subdir

    def save_history(self,
                     history_type: str,
                     data: Union[str, Dict[str, Any]],
                     filename: str | None = None,
                     encrypt: bool | None = None) -> str:
        """
        儲存歷史紀錄

        Args:
            history_type (str): 歷史紀錄類型
            data (Union[str, Dict[str, Any]]): 要儲存的數據
            filename (str): 檔案名稱，如果為None則自動生成
            encrypt (bool): 是否加密，如果為None則使用全局設定

        Returns:
            str: 已儲存的檔案路徑
        """
        # 獲取歷史紀錄目錄
        history_dir = self.get_history_path(history_type)

        # 設定檔案名稱
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.json"
        elif not filename.endswith('.json'):
            filename += '.json'

        # 完整檔案路徑
        file_path = history_dir / filename

        # 決定是否加密
        if encrypt is None:
            encrypt = self.enable_encryption

        try:
            # 準備數據
            if isinstance(data, str):
                save_data = {"content": data, "timestamp": time.time()}
            else:
                save_data = data.copy() if isinstance(data, dict) else {"content": data}
                if "timestamp" not in save_data:
                    save_data["timestamp"] = time.time()

            # 加密
            if encrypt and self.enable_encryption:
                content = encrypt_data(json.dumps(save_data, ensure_ascii=False))
                with open(file_path, 'wb') as f:
                    f.write(content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=4)

            self.logger.debug(f"成功儲存歷史紀錄: {file_path}")
            return str(file_path)
        except Exception as e:
            self.logger.error(f"儲存歷史紀錄失敗: {file_path}, 錯誤: {e}")
            raise

    def load_history(
        self,
        history_type: str,
        filename: str | None = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        讀取歷史紀錄

        Args:
            history_type (str): 歷史紀錄類型
            filename (str): 檔案名稱，如果為None則讀取所有記錄

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: 歷史紀錄數據
        """
        # 獲取歷史紀錄目錄
        history_dir = self.get_history_path(history_type)

        # 讀取特定檔案
        if filename is not None:
            if not filename.endswith('.json'):
                filename += '.json'

            file_path = history_dir / filename

            if not file_path.exists():
                self.logger.warning(f"歷史紀錄檔案不存在: {file_path}")
                return {}

            try:
                # 檢查是否為加密檔案
                with open(file_path, 'rb') as f:
                    content = f.read()

                if self.enable_encryption and encryption_available and is_encrypted(content):
                    # 解密數據
                    decrypted = decrypt_data(content)
                    data = json.loads(decrypted)
                else:
                    # 以文本形式讀取
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                self.logger.debug(f"成功讀取歷史紀錄: {file_path}")
                return data
            except Exception as e:
                self.logger.error(f"讀取歷史紀錄失敗: {file_path}, 錯誤: {e}")
                return {}

        # 讀取所有記錄
        result = []
        try:
            files = sorted(history_dir.glob("*.json"), key=os.path.getmtime, reverse=True)

            for file_path in files:
                try:
                    # 檢查是否為加密檔案
                    with open(file_path, 'rb') as f:
                        content = f.read()

                    if self.enable_encryption and encryption_available and is_encrypted(content):
                        # 解密數據
                        decrypted = decrypt_data(content)
                        data = json.loads(decrypted)
                    else:
                        # 以文本形式讀取
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                    # 添加檔案資訊
                    data["_filename"] = file_path.name
                    data["_filepath"] = str(file_path)
                    result.append(data)
                except Exception as e:
                    self.logger.warning(f"讀取歷史紀錄檔案失敗: {file_path}, 錯誤: {e}")

            self.logger.debug(f"成功讀取歷史紀錄目錄: {history_dir}, 共 {len(result)} 條記錄")
            return result
        except Exception as e:
            self.logger.error(f"讀取歷史紀錄目錄失敗: {history_dir}, 錯誤: {e}")
            return []

    def delete_history(self, history_type: str, filename: str) -> bool:
        """
        刪除歷史紀錄

        Args:
            history_type (str): 歷史紀錄類型
            filename (str): 檔案名稱

        Returns:
            bool: 刪除是否成功
        """
        # 獲取歷史紀錄目錄
        history_dir = self.get_history_path(history_type)

        if not filename.endswith('.json'):
            filename += '.json'

        file_path = history_dir / filename

        if not file_path.exists():
            self.logger.warning(f"要刪除的歷史紀錄不存在: {file_path}")
            return False

        try:
            os.remove(file_path)
            self.logger.debug(f"成功刪除歷史紀錄: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"刪除歷史紀錄失敗: {file_path}, 錯誤: {e}")
            return False

    def clear_history(self, history_type: str) -> int:
        """
        清空特定類型的歷史紀錄

        Args:
            history_type (str): 歷史紀錄類型

        Returns:
            int: 已刪除的檔案數量
        """
        # 獲取歷史紀錄目錄
        history_dir = self.get_history_path(history_type)

        count = 0
        try:
            for file_path in history_dir.glob("*.json"):
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    self.logger.warning(f"刪除檔案失敗: {file_path}, 錯誤: {e}")

            self.logger.debug(f"已清空歷史紀錄目錄: {history_dir}, 共刪除 {count} 個檔案")
            return count
        except Exception as e:
            self.logger.error(f"清空歷史紀錄目錄失敗: {history_dir}, 錯誤: {e}")
            return count

    # ------ 分析結果管理 ------

    def save_analysis_result(self,
                             result: Dict[str, Any],
                             filename: str | None = None,
                             encrypt: bool | None = None) -> str:
        """
        儲存分析結果

        Args:
            result (Dict[str, Any]): 分析結果數據
            filename (str): 檔案名稱，如果為None則自動生成
            encrypt (bool): 是否加密，如果為None則使用全局設定

        Returns:
            str: 已儲存的檔案路徑
        """
        # 確保結果包含時間戳
        if "timestamp" not in result:
            result["timestamp"] = time.time()

        # 使用通用的歷史紀錄保存函數
        return self.save_history("analysis", result, filename, encrypt)

    def load_analysis_result(self, filename: str) -> Dict[str, Any]:
        """
        讀取分析結果

        Args:
            filename (str): 檔案名稱

        Returns:
            Dict[str, Any]: 分析結果數據
        """
        return self.load_history("analysis", filename)

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """
        獲取所有分析結果歷史

        Returns:
            List[Dict[str, Any]]: 分析結果歷史列表
        """
        return self.load_history("analysis")

    # ------ 匯入匯出功能 ------
    def export_to_json(self,
                       data: Dict[str, Any],
                       filepath: str,
                       indent: int = 4,
                       encrypt: bool = False) -> bool:
        """
        將數據匯出為JSON文件

        Args:
            data (Dict[str, Any]): 要匯出的數據
            filepath (str): 輸出文件路徑
            indent (int): JSON縮排空格數
            encrypt (bool): 是否加密

        Returns:
            bool: 匯出是否成功
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # 加密
            if encrypt and self.enable_encryption:
                content = encrypt_data(json.dumps(data, ensure_ascii=False))
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=indent)

            self.logger.debug(f"成功匯出JSON檔案: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"匯出JSON檔案失敗: {filepath}, 錯誤: {e}")
            return False

    def export_to_text(self,
                       data: str,
                       filepath: str,
                       encoding: str = 'utf-8',
                       encrypt: bool = False) -> bool:
        """
        將數據匯出為文本文件

        Args:
            data (str): 要匯出的數據
            filepath (str): 輸出文件路徑
            encoding (str): 檔案編碼
            encrypt (bool): 是否加密

        Returns:
            bool: 匯出是否成功
        """
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            # 加密
            if encrypt and self.enable_encryption:
                content = encrypt_data(data)
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(data)

            self.logger.debug(f"成功匯出文本檔案: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"匯出文本檔案失敗: {filepath}, 錯誤: {e}")
            return False

    def import_from_json(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        從JSON文件匯入數據

        Args:
            filepath (str): 輸入文件路徑

        Returns:
            Optional[Dict[str, Any]]: 匯入的數據，失敗時返回None
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"要匯入的檔案不存在: {filepath}")
            return None

        try:
            # 檢查是否為加密檔案
            with open(filepath, 'rb') as f:
                content = f.read()

            if self.enable_encryption and encryption_available and is_encrypted(content):
                # 解密數據
                decrypted = decrypt_data(content)
                data = json.loads(decrypted)
            else:
                # 以文本形式讀取
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            self.logger.debug(f"成功匯入JSON檔案: {filepath}")
            return data
        except json.JSONDecodeError:
            self.logger.error(f"匯入的檔案不是有效的JSON格式: {filepath}")
            return None
        except Exception as e:
            self.logger.error(f"匯入JSON檔案失敗: {filepath}, 錯誤: {e}")
            return None

    def import_from_text(self, filepath: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        從文本文件匯入數據

        Args:
            filepath (str): 輸入文件路徑
            encoding (str): 檔案編碼

        Returns:
            Optional[str]: 匯入的數據，失敗時返回None
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"要匯入的檔案不存在: {filepath}")
            return None

        try:
            # 檢查是否為加密檔案
            with open(filepath, 'rb') as f:
                content = f.read()

            if self.enable_encryption and encryption_available and is_encrypted(content):
                # 解密數據
                data = decrypt_data(content)
            else:
                # 以文本形式讀取
                with open(filepath, 'r', encoding=encoding) as f:
                    data = f.read()

            self.logger.debug(f"成功匯入文本檔案: {filepath}")
            return data
        except Exception as e:
            self.logger.error(f"匯入文本檔案失敗: {filepath}, 錯誤: {e}")
            return None

    # ------ 工具函數 ------

    def backup_file(self, filepath: str, backup_suffix: str = '.backup') -> Optional[str]:
        """
        備份文件

        Args:
            filepath (str): 要備份的文件路徑
            backup_suffix (str): 備份文件後綴

        Returns:
            Optional[str]: 備份文件路徑，失敗時返回None
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"要備份的檔案不存在: {filepath}")
            return None

        backup_path = filepath + backup_suffix
        try:
            shutil.copy2(filepath, backup_path)
            self.logger.debug(f"成功備份檔案: {filepath} -> {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"備份檔案失敗: {filepath}, 錯誤: {e}")
            return None

    def file_exists(self, filepath: str) -> bool:
        """
        檢查文件是否存在

        Args:
            filepath (str): 文件路徑

        Returns:
            bool: 文件是否存在
        """
        return os.path.exists(filepath)

    def get_file_size(self, filepath: str) -> int:
        """
        獲取文件大小

        Args:
            filepath (str): 文件路徑

        Returns:
            int: 文件大小（字節）
        """
        if not os.path.exists(filepath):
            return 0
        return os.path.getsize(filepath)

    def get_file_modification_time(self, filepath: str) -> float:
        """
        獲取文件最後修改時間

        Args:
            filepath (str): 文件路徑

        Returns:
            float: 最後修改時間（時間戳）
        """
        if not os.path.exists(filepath):
            return 0
        return os.path.getmtime(filepath)


# 直接執行文件時的測試程式
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 創建檔案管理器
    file_manager = FileManager()

    # 測試資源檔案讀寫
    resource_test = {"test": True, "message": "這是一個測試資源檔案", "timestamp": time.time()}

    # 儲存測試資源
    file_manager.save_resource_json("test/resource_test.json", resource_test)

    # 讀取測試資源
    loaded_resource = file_manager.load_resource_json("test/resource_test.json")
    print("讀取的資源檔案:", loaded_resource)

    # 測試歷史紀錄
    test_history = {"input_type": "test", "data": "測試數據", "score": 100}

    # 儲存測試歷史
    history_path = file_manager.save_history("test", test_history)
    print("已儲存歷史紀錄:", history_path)

    # 讀取測試歷史
    loaded_history = file_manager.load_history("test")
    print("讀取的歷史紀錄:", loaded_history)

    # 測試分析結果
    test_result = {
        "input_type": "姓名",
        "input_value": "測試姓名",
        "counts": {
            "天醫": 2,
            "生氣": 1
        },
        "recommendations": ["1234", "5678"]
    }

    # 儲存測試結果
    result_path = file_manager.save_analysis_result(test_result)
    print("已儲存分析結果:", result_path)

    # 讀取測試結果
    loaded_result = file_manager.load_analysis_result(os.path.basename(result_path))
    print("讀取的分析結果:", loaded_result)

    # 測試匯出
    export_path = os.path.join(os.path.expanduser("~"), "Desktop", "test_export.json")
    file_manager.export_to_json(test_result, export_path)
    print("已匯出測試檔案:", export_path)
