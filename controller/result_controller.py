# controller/result_controller.py
"""
數字DNA分析器 - 結果控制器
負責處理分析結果，管理結果展示和儲存：
1. 接收來自analysis_controller的分析結果
2. 儲存結果到歷史記錄
3. 格式化結果並傳遞給UI模組顯示
4. 管理結果匯出功能
"""

import logging
import json
import os
import datetime
from tkinter import messagebox
from data.file_manager import FileManager
from controller.input_controller import save_input_history

logger = logging.getLogger("數字DNA分析器.ResultController")


class ResultController:

    def __init__(self):
        """初始化結果控制器"""
        self.logger = logging.getLogger("數字DNA分析器.ResultController")
        self.logger.info("初始化結果控制器")

        # 儲存當前分析結果
        self.current_result = None

        # 檔案管理實例化
        self.file_manager = FileManager()

        # 歷史記錄路徑
        self.history_dir = self.file_manager.history_dir
        # self.history_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        #                                "data", "history")
        # os.makedirs(self.history_dir, exist_ok=True)

    def process_result(self, result_data, input_data=None, display_callback=None):
        """
        處理分析結果並交由UI顯示

        Args:
            result_data (dict): 分析結果字典
            input_data (dict): 輸入數據，用於保存輸入歷史
            display_callback (function): 顯示函數回調
        """
        if not result_data:
            self.logger.warning("接收到空的分析結果")
            return

        self.logger.info(f"處理分析結果: {result_data.get('input_type', '未知類型')}")

        # 保存當前結果
        self.current_result = result_data

        # 如果有錯誤訊息，顯示警告
        if result_data.get("messages"):
            self.logger.warning(f"分析中有警告: {', '.join(result_data['messages'])}")
            messagebox.showwarning("分析警告", "\n".join(result_data['messages']))

        # 保存輸入歷史
        if input_data:
            save_input_history(input_data, self.file_manager)

        # 如果提供了顯示，調用更新UI
        if display_callback:
            display_callback(result_data)

        # 自動保存到歷史記錄
        self.save_to_history(result_data)

        return result_data

    def save_result_to_history(self, result_data):
        """
        將分析結果保存到歷史記錄

        使用FileManager來保存，避免重複實現檔案保存邏輯

        Args:
            result_data (dict): 分析結果字典

        Returns:
            str: 保存的文件路徑
        """
        try:
            # 使用FileManager保存分析結果
            filepath = self.file_manager.save_analysis_result(result_data)
            self.logger.info(f"已儲存分析結果到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"儲存分析結果失敗: {e}", exc_info=True)
            return None

    def save_to_history(self, result_data, filename=None):
        """
        將結果保存到歷史記錄(保留儲存方法)

        Args:
            result_data (dict): 分析結果字典
            filename (str): 可選的自定義文件名

        Returns:
            str: 保存的文件路徑
        """
        try:
            # 生成時間戳記作為檔案名稱的一部分
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            input_type = result_data.get("input_type", "未知")

            # 如果沒有提供檔案名稱，則自動生成
            if not filename:
                filename = f"{input_type}_{timestamp}.json"

            # 確保檔案名稱有.json副檔名
            if not filename.endswith('.json'):
                filename += '.json'

            # 組合完整路徑
            filepath = os.path.join(self.history_dir, filename)

            # 創建一個可序列化的結果副本
            serializable_data = self._prepare_data_for_json(result_data)

            # 儲存結果到JSON檔案
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"已儲存結果到: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"儲存歷史記錄失敗: {e}", exc_info=True)
            return None

    def _prepare_data_for_json(self, data):
        """
        將數據準備為可JSON序列化的格式

        Args:
            data: 任何數據類型

        Returns:
            轉換後的JSON可序列化數據
        """
        if isinstance(data, dict):
            return {k: self._prepare_data_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, tuple):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, set):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        else:
            # 嘗試轉換為字符串
            return str(data)

    def load_from_history(self, filepath, display_callback=None):
        """
        從歷史記錄載入分析結果

        Args:
            filepath (str): 歷史記錄檔案路徑
            display_callback (function): 顯示函數回調

        Returns:
            dict: 載入的分析結果
        """
        try:
            self.logger.info(f"載入歷史記錄: {filepath}")

            # 檢查檔案是否存在
            if not os.path.exists(filepath):
                self.logger.error(f"檔案不存在: {filepath}")
                return None
            # 使用FileManager載入
            if filepath.startswith(str(self.file_manager.history_dir / "analysis")):
                # 提取檔案名稱
                filename = os.path.basename(filepath)
                result_data = self.file_manager.load_analysis_result(filename)
            else:
                # 載入JSON檔案
                with open(filepath, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)

            # 更新當前結果
            self.current_result = result_data

            # 如果提供了顯示回調，調用它來更新UI
            if display_callback:
                display_callback(result_data)

            return result_data

        except Exception as e:
            self.logger.error(f"載入歷史記錄失敗: {e}", exc_info=True)
            return None

    def list_history(self, input_type=None):
        """
        列出歷史記錄檔案

        Args:
            input_type (str): 可選的輸入類型過濾

        Returns:
            list: 歷史記錄檔案列表
        """
        try:
            # 使用FileManager獲取分析歷史
            history_records = self.file_manager.get_analysis_history()

            # 轉換為需要的格式
            history_files = []
            for record in history_records:
                filename = record.get("_filename", "")
                filepath = record.get("_filepath", "")

                # 如果指定了輸入類型，則進行過濾
                if input_type and record.get("input_type") != input_type:
                    continue

                # 獲取時間戳
                timestamp = record.get("timestamp", 0)

                history_files.append({
                    'filename':
                    filename,
                    'filepath':
                    filepath,
                    'mtime':
                    timestamp,
                    'datetime':
                    datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    'input_type':
                    record.get("input_type", "未知")
                })
        # try:
        #     history_files = []

        #     # 列出歷史目錄中的所有JSON檔案
        #     for filename in os.listdir(self.history_dir):
        #         if filename.endswith('.json'):
        #             # 如果指定了輸入類型，則進行過濾
        #             if input_type and not filename.startswith(f"{input_type}_"):
        #                 continue

        #             filepath = os.path.join(self.history_dir, filename)
        #             mtime = os.path.getmtime(filepath)
        #             history_files.append({
        #                 'filename': filename,
        #                 'filepath': filepath,
        #                 'mtime': mtime,
        #                 'datetime': datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        #             })

        # 按修改時間排序，最新的在前
            history_files.sort(key=lambda x: x['mtime'], reverse=True)

            return history_files

        except Exception as e:
            self.logger.error(f"列出歷史記錄失敗: {e}", exc_info=True)
            return []

    def delete_history(self, filepath):
        """
        刪除歷史記錄檔案

        Args:
            filepath (str): 歷史記錄檔案路徑

        Returns:
            bool: 是否刪除成功
        """
        try:
            # 如果是分析歷史目錄中的檔案，使用FileManager刪除
            if filepath.startswith(str(self.file_manager.history_dir / "analysis")):
                filename = os.path.basename(filepath)
                return self.file_manager.delete_history("analysis", filename)

            # 其他檔案使用原始方法刪除
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"已刪除歷史記錄: {filepath}")
                return True
            else:
                self.logger.warning(f"檔案不存在，無法刪除: {filepath}")
                return False

        except Exception as e:
            self.logger.error(f"刪除歷史記錄失敗: {e}", exc_info=True)
            return False

    def format_result_for_display(self, result_data):
        """
        格式化分析結果用於顯示

        Args:
            result_data (dict): 分析結果字典

        Returns:
            dict: 格式化後的結果
        """
        # 複製結果以避免修改原始數據
        formatted = result_data.copy()

        # 添加基本統計
        formatted['summary'] = {
            'total_fields':
            sum(result_data.get('counts', {}).values()),
            'adjusted_fields':
            sum(result_data.get('adjusted_counts', {}).values()),
            'positive_fields_count':
            sum(1 for field in ['天醫', '生氣', '延年', '伏位']
                if field in result_data.get('adjusted_counts', {})),
            'negative_fields_count':
            sum(1 for field in ['五鬼', '六煞', '禍害', '絕命']
                if field in result_data.get('adjusted_counts', {}))
        }

        # 格式化各個磁場的詳細資訊
        formatted['formatted_fields'] = {}
        for field, details in result_data.get('field_details', {}).items():
            formatted['formatted_fields'][field] = {
                'count':
                details.get('count', 0),
                'keywords':
                '、'.join(details.get('keywords', []))
                if isinstance(details.get('keywords'), list) else details.get('keywords', ''),
                'strengths':
                details.get('strengths', ''),
                'weaknesses':
                details.get('weaknesses', ''),
                'financial_strategy':
                details.get('financial_strategy', ''),
                'relationship_advice':
                details.get('relationship_advice', '')
            }

        # 格式化調整日誌
        if 'adjust_log' in result_data:
            formatted['formatted_adjust_log'] = ' '.join(result_data['adjust_log'])

        return formatted

    def export_result(self, filepath, format_type='json'):
        """
        匯出分析結果

        Args:
            filepath (str): 匯出檔案路徑
            format_type (str): 匯出格式 ('json' 或 'txt')

        Returns:
            bool: 是否匯出成功
        """
        if not self.current_result:
            self.logger.warning("沒有當前結果可匯出")
            return False

        try:
            # 根據格式類型選擇匯出方式
            if format_type.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result, f, ensure_ascii=False, indent=2)

            elif format_type.lower() == 'txt':
                # 格式化為可讀文字格式
                formatted = self.format_result_for_display(self.current_result)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"數字DNA分析結果\n")
                    f.write(f"===================\n\n")

                    f.write(f"輸入類型: {formatted.get('input_type', '未知')}\n\n")

                    f.write("原始磁場統計:\n")
                    for field, count in formatted.get('counts', {}).items():
                        f.write(f"  {field}: {count}\n")

                    f.write("\n進階調整:\n")
                    f.write(f"  {formatted.get('formatted_adjust_log', '無調整')}\n")

                    f.write("\n調整後磁場統計:\n")
                    for field, count in formatted.get('adjusted_counts', {}).items():
                        f.write(f"  {field}: {count}\n")

                    f.write("\n推薦幸運數字:\n")
                    for idx, num in enumerate(formatted.get('recommendations', []), 1):
                        f.write(f"  {idx}. {num}\n")

                    f.write("\n磁場詳細資訊:\n")
                    for field, details in formatted.get('formatted_fields', {}).items():
                        f.write(f"  {field} (出現 {details['count']} 次)\n")
                        f.write(f"    關鍵字: {details['keywords']}\n")
                        f.write(f"    優勢: {details['strengths']}\n")
                        f.write(f"    弱點: {details['weaknesses']}\n")
                        f.write(f"    財務建議: {details['financial_strategy']}\n")
                        f.write(f"    關係建議: {details['relationship_advice']}\n\n")

            else:
                self.logger.error(f"不支援的匯出格式: {format_type}")
                return False

            self.logger.info(f"成功匯出結果到: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"匯出結果失敗: {e}", exc_info=True)
            return False


# 如果直接執行此模組，運行一個簡單的測試
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    controller = ResultController()

    # 建立一個測試結果
    test_result = {
        "input_type": "姓名",
        "raw_analysis": "天醫 生氣 延年 五鬼",
        "counts": {
            "天醫": 1,
            "生氣": 1,
            "延年": 1,
            "五鬼": 1
        },
        "adjusted_counts": {
            "天醫": 1,
            "生氣": 1,
            "延年": 1
        },
        "adjust_log": ["(天醫-0)", "(生氣-0)", "(延年-0)", "(五鬼-1)"],
        "recommendations": ["1234", "5678", "9012"],
        "field_details": {
            "天醫": {
                "count": 1,
                "keywords": ["主大才", "天生聰穎", "文筆好"],
                "strengths": "賺錢有如神助、諸事順遂、外型氣質俱佳",
                "weaknesses": "極度善良，偶爾會被蒙騙",
                "financial_strategy": "智慧投資，行善積福，防範詐騙",
                "relationship_advice": "關懷對方，共同成長，給予情感支持"
            }
        }
    }

    # 處理結果並儲存
    controller.process_result(test_result)

    # 列出歷史記錄
    history = controller.list_history()
    print(f"歷史記錄數: {len(history)}")

    # 測試格式化與匯出
    if history:
        first_file = history[0]['filepath']
        loaded = controller.load_from_history(first_file)
        if loaded:
            formatted = controller.format_result_for_display(loaded)
            print("格式化成功!")
