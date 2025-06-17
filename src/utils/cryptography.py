import os

from cryptography.fernet import Fernet

from .file_manager import FileManager


class AESEncryptionFernet:

    def __init__(self, file_manager: FileManager):
        key = self.generate_key(file_manager)
        self.fernet = Fernet(key)

    def encrypt(self, message: str):
        """將明文加密成密文"""
        encrypted = self.fernet.encrypt(message.encode()).decode()
        return encrypted

    def decrypt(self, encrypted_data: str) -> str:
        """將密文解密成明文"""
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def generate_key(self, file_manager: FileManager) -> bytes:
        """產生密鑰"""
        key_path = file_manager.get_key_path()
        if os.path.exists(key_path):
            key = file_manager.load_from_data_file(key_path)
        else:
            key = Fernet.generate_key()
            file_manager.dump_to_data_file(key_path, key)

        return key
