#  app/__init__.py
"""
數字DNA分析器 - 主應用程式模組
提供應用程式的主類別和入口點

此模組包含：
1. 應用程式主類別 (number_dna_app.py)
2. 應用程式初始化和配置
"""

# 導入應用程式主類別
from app.number_dna_app import NumberDnaApp

# 定義版本
__version__ = "1.0.0"

# 定義公開的API
__all__ = ['NumberDnaApp']

# 應用程式創建函數
def create_app(config_path=None):
    """
    創建應用程式實例

    Args:
        config_path (str, optional): 配置文件路徑

    Returns:
        NumberDnaApp: 應用程式實例
    """
    # 初始化應用
    app = NumberDnaApp(config_path)

    return app

# 檢查所需依賴
def check_dependencies():
    """
    檢查必要的依賴是否已安裝

    Returns:
        tuple: (依賴是否滿足, 缺少的依賴列表)
    """
    missing_deps = []

    # 檢查 cryptography
    try:
        import cryptography
        crypto_version = cryptography.__version__
    except ImportError:
        missing_deps.append("cryptography (數據加密功能將被禁用)")

    # 檢查 matplotlib (可選)
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib (視覺化功能將被禁用)")

    # 檢查 Pillow (可選)
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow (圖像處理功能將被禁用)")

    return len(missing_deps) == 0, missing_deps