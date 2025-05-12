#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
數字DNA分析器 - 主應用程式類
管理應用程式生命週期與模組協調
"""

import tkinter as tk
from tkinter import messagebox
import logging
import sys
from pathlib import Path

# 確保可以匯入其他模組
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 匯入相關模組
from core.analyzer import DigitalAnalyzer
from core.energy_calculator import EnergyCalculator
from core.number_generator import NumberGenerator
from data.file_manager import FileManager
from data.encryption import EncryptionService
from data.rule_repository import RuleRepository
from ui.main_window import MainWindow
from utils.config import ConfigManager


class DigitalDnaApp(tk.Tk):
    """數字DNA分析器主應用程式類"""

    def __init__(self, config_manager):
        """初始化應用程式"""
        super().__init__()

        self.logger = logging.getLogger("數字DNA分析器.App")
        self.logger.info("初始化主應用程式")

        self.config_manager = config_manager

        # 初始化資料模組
        self._init_data_modules()

        # 初始化核心模組
        self._init_core_modules()

        # 初始化UI模組
        self._init_ui()

        # 綁定應用程式關閉事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.logger.info("應用程式初始化完成")

    def _init_data_modules(self):
        """初始化資料相關模組"""
        self.logger.info("初始化資料模組")

        try:
            # 初始化加密服務
            self.encryption_service = EncryptionService()

            # 初始化檔案管理器
            self.file_manager = FileManager(self.encryption_service)

            # 初始化規則庫
            self.rule_repository = RuleRepository()
            self.rule_repository.load_rules()

        except Exception as e:
            self.logger.error(f"資料模組初始化失敗: {e}", exc_info=True)
            messagebox.showerror("初始化錯誤", f"無法初始化資料模組: {e}")
            sys.exit(1)

    def _init_core_modules(self):
        """初始化核心分析模組"""
        self.logger.info("初始化核心模組")

        try:
            # 初始化能量計算器
            self.energy_calculator = EnergyCalculator(self.rule_repository)

            # 初始化數字分析器
            self.analyzer = DigitalAnalyzer(self.rule_repository, self.energy_calculator)

            # 初始化數字生成器
            self.number_generator = NumberGenerator(self.analyzer, self.energy_calculator)

        except Exception as e:
            self.logger.error(f"核心模組初始化失敗: {e}", exc_info=True)
            messagebox.showerror("初始化錯誤", f"無法初始化核心模組: {e}")
            sys.exit(1)

    def _init_ui(self):
        """初始化用戶界面"""
        self.logger.info("初始化用戶界面")

        try:
            # 創建主窗口
            self.main_window = MainWindow(self, self.analyzer, self.number_generator,
                                         self.file_manager, self.rule_repository)

            # 應用設定
            self._apply_settings()

        except Exception as e:
            self.logger.error(f"UI初始化失敗: {e}", exc_info=True)
            messagebox.showerror("初始化錯誤", f"無法初始化用戶界面: {e}")
            sys.exit(1)

    def _apply_settings(self):
        """應用用戶設定"""
        settings = self.config_manager.get_settings()

        # 應用主題
        theme = settings.get("theme", "default")
        if theme != "default":
            try:
                self.tk.call("source", f"themes/{theme}.tcl")
                self.tk.call("set_theme", theme)
            except tk.TclError:
                self.logger.warning(f"無法載入主題: {theme}")

        # 應用其他設定...

    def _on_closing(self):
        """處理應用程式關閉事件"""
        self.logger.info("應用程式關閉")

        # 儲存當前設定
        try:
            self.config_manager.save_settings()
        except Exception as e:
            self.logger.error(f"儲存設定失敗: {e}")

        # 關閉應用程式
        self.destroy()
