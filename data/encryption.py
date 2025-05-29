# data/encryption.py
"""
數字DNA分析器 - 加密服務模組
提供數據加密與解密功能

功能：
1. 提供敏感數據的加密與解密功能
2. 管理加密金鑰的生成和儲存
3. 保護使用者歷史記錄和個人資訊
4. 確保儲存數據的安全性
5. 支援加密檔案的識別和處理
"""

import os
import base64
import logging
from pathlib import Path
from typing import Union, Optional, BinaryIO
import json

# 設定日誌記錄器
logger = logging.getLogger("數字DNA分析器.Encryption")

# 嘗試載入加密庫，如果不可用則降級處理
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    cryptography_available = True
except ImportError:
    logger.warning("無法載入加密庫 cryptography，將使用基礎編碼代替加密（不安全）")
    cryptography_available = False

# 加密標頭，用於識別加密數據
ENCRYPTION_HEADER = b"NDNA_ENC_"

class EncryptionService:
    """加密服務類，提供數據加密與解密功能"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """單例模式，確保全局只有一個加密服務實例"""
        if cls._instance is None:
            cls._instance = super(EncryptionService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, key_path: str = None, password: str = None):
        """
        初始化加密服務

        Args:
            key_path (str): 金鑰檔案路徑，如果為None則使用預設路徑
            password (str): 密碼，用於生成金鑰
        """
        # 避免重複初始化
        if self.initialized:
            return

        self.logger = logging.getLogger("數字DNA分析器.Encryption")

        # 設定金鑰路徑
        if key_path is None:
            base_dir = Path(__file__).parent.parent
            self.key_path = os.path.join(base_dir, "data", "config", "encryption.key")
        else:
            self.key_path = key_path

        # 確保目錄存在
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)

        # 檢查加密庫是否可用
        self.cryptography_available = cryptography_available

        if not self.cryptography_available:
            self.logger.warning("加密庫不可用，將使用基礎編碼（不安全）")
            self.cipher = None
        else:
            # 載入或生成金鑰
            self.cipher = self._load_or_generate_key(password)

        self.initialized = True
        self.logger.info("加密服務初始化完成")

    def _load_or_generate_key(self, password: Optional[str] = None) -> Optional[Fernet]:
        """
        載入或生成加密金鑰

        Args:
            password (str): 用於生成金鑰的密碼

        Returns:
            Fernet: 加密器實例
        """
        try:
            if os.path.exists(self.key_path):
                # 載入現有金鑰
                with open(self.key_path, "rb") as key_file:
                    key = key_file.read()
                self.logger.debug(f"已從 {self.key_path} 載入加密金鑰")
            else:
                # 生成新金鑰
                if password:
                    # 基於密碼生成金鑰
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

                    # 儲存鹽值以便未來使用
                    with open(f"{self.key_path}.salt", "wb") as salt_file:
                        salt_file.write(salt)
                else:
                    # 隨機生成金鑰
                    key = Fernet.generate_key()

                # 儲存金鑰
                with open(self.key_path, "wb") as key_file:
                    key_file.write(key)

                self.logger.info(f"已生成新的加密金鑰並儲存到 {self.key_path}")

            return Fernet(key)
        except Exception as e:
            self.logger.error(f"載入或生成金鑰失敗: {e}")
            return None

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        加密數據

        Args:
            data (Union[str, bytes]): 要加密的數據

        Returns:
            bytes: 加密後的數據
        """
        # 確保數據為bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        try:
            # 使用加密庫加密
            if self.cryptography_available and self.cipher:
                encrypted = self.cipher.encrypt(data_bytes)
                # 添加標頭以標識數據已加密
                return ENCRYPTION_HEADER + encrypted
            else:
                # 降級處理：使用base64編碼
                self.logger.warning("使用基礎編碼代替加密（不安全）")
                encoded = base64.b64encode(data_bytes)
                return ENCRYPTION_HEADER + encoded
        except Exception as e:
            self.logger.error(f"加密數據失敗: {e}")
            # 發生錯誤時返回原始數據
            return data_bytes

    def decrypt(self, data: bytes) -> bytes:
        """
        解密數據

        Args:
            data (bytes): 要解密的數據

        Returns:
            bytes: 解密後的數據
        """
        # 檢查數據是否有加密標頭
        if not data.startswith(ENCRYPTION_HEADER):
            # 未加密，直接返回
            return data

        # 移除標頭
        encrypted_data = data[len(ENCRYPTION_HEADER):]

        try:
            # 使用加密庫解密
            if self.cryptography_available and self.cipher:
                return self.cipher.decrypt(encrypted_data)
            else:
                # 降級處理：使用base64解碼
                self.logger.warning("使用基礎解碼代替解密（不安全）")
                return base64.b64decode(encrypted_data)
        except Exception as e:
            self.logger.error(f"解密數據失敗: {e}")
            # 發生錯誤時返回原始數據
            return data

    def encrypt_file(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        加密檔案

        Args:
            input_path (str): 輸入檔案路徑
            output_path (str, optional): 輸出檔案路徑，如果為None則覆蓋輸入檔案

        Returns:
            bool: 加密是否成功
        """
        if output_path is None:
            output_path = input_path

        try:
            # 讀取檔案
            with open(input_path, "rb") as f:
                data = f.read()

            # 加密數據
            encrypted = self.encrypt(data)

            # 寫入檔案
            with open(output_path, "wb") as f:
                f.write(encrypted)

            self.logger.debug(f"已加密檔案: {input_path} -> {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"加密檔案失敗: {input_path}, 錯誤: {e}")
            return False

    def decrypt_file(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        解密檔案

        Args:
            input_path (str): 輸入檔案路徑
            output_path (str, optional): 輸出檔案路徑，如果為None則覆蓋輸入檔案

        Returns:
            bool: 解密是否成功
        """
        if output_path is None:
            output_path = input_path

        try:
            # 讀取檔案
            with open(input_path, "rb") as f:
                data = f.read()

            # 檢查是否已加密
            if not data.startswith(ENCRYPTION_HEADER):
                self.logger.warning(f"檔案未加密: {input_path}")
                if input_path != output_path:
                    # 如果輸出路徑不同，則複製檔案
                    with open(output_path, "wb") as f:
                        f.write(data)
                return True

            # 解密數據
            decrypted = self.decrypt(data)

            # 寫入檔案
            with open(output_path, "wb") as f:
                f.write(decrypted)

            self.logger.debug(f"已解密檔案: {input_path} -> {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"解密檔案失敗: {input_path}, 錯誤: {e}")
            return False

    def encrypt_json(self, data: dict) -> bytes:
        """
        加密JSON數據

        Args:
            data (dict): 要加密的JSON數據

        Returns:
            bytes: 加密後的數據
        """
        try:
            # 轉換為JSON字串
            json_str = json.dumps(data, ensure_ascii=False)

            # 加密數據
            return self.encrypt(json_str)
        except Exception as e:
            self.logger.error(f"加密JSON數據失敗: {e}")
            return b""

    def decrypt_json(self, data: bytes) -> dict:
        """
        解密JSON數據

        Args:
            data (bytes): 要解密的數據

        Returns:
            dict: 解密後的JSON數據
        """
        try:
            # 解密數據
            decrypted = self.decrypt(data)

            # 解析JSON
            return json.loads(decrypted)
        except Exception as e:
            self.logger.error(f"解密JSON數據失敗: {e}")
            return {}

    def is_data_encrypted(self, data: bytes) -> bool:
        """
        檢查數據是否已加密

        Args:
            data (bytes): 要檢查的數據

        Returns:
            bool: 數據是否已加密
        """
        return data.startswith(ENCRYPTION_HEADER)

    def is_file_encrypted(self, file_path: str) -> bool:
        """
        檢查檔案是否已加密

        Args:
            file_path (str): 檔案路徑

        Returns:
            bool: 檔案是否已加密
        """
        try:
            # 讀取檔案頭部
            with open(file_path, "rb") as f:
                header = f.read(len(ENCRYPTION_HEADER))

            return header == ENCRYPTION_HEADER
        except Exception as e:
            self.logger.error(f"檢查檔案加密狀態失敗: {file_path}, 錯誤: {e}")
            return False

    def change_password(self, new_password: str) -> bool:
        """
        變更加密密碼

        Args:
            new_password (str): 新密碼

        Returns:
            bool: 變更是否成功
        """
        if not self.cryptography_available:
            self.logger.warning("加密庫不可用，無法變更密碼")
            return False

        try:
            # 生成新的金鑰
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(new_password.encode()))

            # 儲存鹽值
            with open(f"{self.key_path}.salt", "wb") as salt_file:
                salt_file.write(salt)

            # 儲存金鑰
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)

            # 更新加密器
            self.cipher = Fernet(key)

            self.logger.info("已成功變更加密密碼")
            return True
        except Exception as e:
            self.logger.error(f"變更加密密碼失敗: {e}")
            return False

# 全局實例
_encryption_service = None

def initialize(key_path: str = None, password: str = None) -> EncryptionService:
    """
    初始化加密服務

    Args:
        key_path (str): 金鑰檔案路徑
        password (str): 密碼

    Returns:
        EncryptionService: 加密服務實例
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService(key_path, password)
    return _encryption_service

def get_encryption_service() -> EncryptionService:
    """
    獲取加密服務實例

    Returns:
        EncryptionService: 加密服務實例
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service

def encrypt_data(data: Union[str, bytes]) -> bytes:
    """
    加密數據

    Args:
        data (Union[str, bytes]): 要加密的數據

    Returns:
        bytes: 加密後的數據
    """
    return get_encryption_service().encrypt(data)

def decrypt_data(data: bytes) -> bytes:
    """
    解密數據

    Args:
        data (bytes): 要解密的數據

    Returns:
        bytes: 解密後的數據
    """
    return get_encryption_service().decrypt(data)

def encrypt_json(data: dict) -> bytes:
    """
    加密JSON數據

    Args:
        data (dict): 要加密的JSON數據

    Returns:
        bytes: 加密後的數據
    """
    return get_encryption_service().encrypt_json(data)

def decrypt_json(data: bytes) -> dict:
    """
    解密JSON數據

    Args:
        data (bytes): 要解密的數據

    Returns:
        dict: 解密後的JSON數據
    """
    return get_encryption_service().decrypt_json(data)

def is_encrypted(data: bytes) -> bool:
    """
    檢查數據是否已加密

    Args:
        data (bytes): 要檢查的數據

    Returns:
        bool: 數據是否已加密
    """
    return data.startswith(ENCRYPTION_HEADER)

def encrypt_file(input_path: str, output_path: Optional[str] = None) -> bool:
    """
    加密檔案

    Args:
        input_path (str): 輸入檔案路徑
        output_path (str, optional): 輸出檔案路徑

    Returns:
        bool: 加密是否成功
    """
    return get_encryption_service().encrypt_file(input_path, output_path)

def decrypt_file(input_path: str, output_path: Optional[str] = None) -> bool:
    """
    解密檔案

    Args:
        input_path (str): 輸入檔案路徑
        output_path (str, optional): 輸出檔案路徑

    Returns:
        bool: 解密是否成功
    """
    return get_encryption_service().decrypt_file(input_path, output_path)

def is_file_encrypted(file_path: str) -> bool:
    """
    檢查檔案是否已加密

    Args:
        file_path (str): 檔案路徑

    Returns:
        bool: 檔案是否已加密
    """
    return get_encryption_service().is_file_encrypted(file_path)

def change_password(new_password: str) -> bool:
    """
    變更加密密碼

    Args:
        new_password (str): 新密碼

    Returns:
        bool: 變更是否成功
    """
    return get_encryption_service().change_password(new_password)

# 測試用程式
if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 初始化加密服務
    encryption_service = initialize()

    # 測試字串加密解密
    test_str = "這是一個測試字串"
    encrypted = encrypt_data(test_str)
    decrypted = decrypt_data(encrypted)

    print(f"原始字串: {test_str}")
    print(f"加密後: {encrypted}")
    print(f"解密後: {decrypted.decode('utf-8')}")
    print(f"加密標記: {is_encrypted(encrypted)}")

    # 測試JSON加密解密
    test_json = {
        "name": "測試使用者",
        "age": 30,
        "data": [1, 2, 3, 4, 5]
    }

    encrypted_json = encrypt_json(test_json)
    decrypted_json = decrypt_json(encrypted_json)

    print(f"\n原始JSON: {test_json}")
    print(f"加密後: {encrypted_json}")
    print(f"解密後: {decrypted_json}")

    # 測試檔案加密解密（僅當運行在本地環境時）
    if os.path.exists("test.txt"):
        print("\n測試檔案加密解密:")
        encrypt_file("test.txt", "test.enc")
        print(f"檔案加密標記: {is_file_encrypted('test.enc')}")
        decrypt_file("test.enc", "test.dec")

        # 讀取原始檔案和解密後檔案進行比較
        with open("test.txt", "rb") as f:
            original = f.read()
        with open("test.dec", "rb") as f:
            decrypted = f.read()

        print(f"檔案比較: {'相同' if original == decrypted else '不同'}")
