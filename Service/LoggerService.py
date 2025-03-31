from loguru import logger
import os
import threading
from Config import Config
class LoggerService:
    _instance = None  # 单例
    _lock = threading.Lock()  # 线程安全

    def __new__(cls):
        """单例模式，确保 LoggerService 只初始化一次"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerService, cls).__new__(cls)
                cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        config = Config()
        """初始化日志配置"""
        # 创建日志目录（如果不存在）
        os.makedirs(os.path.dirname(config.get("Logging","business_log")), exist_ok=True)
        os.makedirs(os.path.dirname(config.get("Logging","download_log")), exist_ok=True)
        os.makedirs(os.path.dirname(config.get("Logging","database_log")), exist_ok=True)

        # 移除默认 Logger
        logger.remove()

        # 添加业务日志（普通业务日志）
        logger.add(
            config.get("Logging","business_log"),
            rotation=config.get("Logging","rotation"),
            retention=config.get("Logging","retention"),
            level=config.get("Logging","level"),
            format=config.get("Logging","format"),
            filter=lambda record: record["extra"].get("category") == "business"
        )

        # 添加数据库日志（数据库日志）
        logger.add(
            config.get("Logging","database_log"),
            rotation=config.get("Logging","rotation"),
            retention=config.get("Logging","retention"),
            level=config.get("Logging","level"),
            format=config.get("Logging","format"),
            filter=lambda record: record["extra"].get("category") == "database"
        )

        # 添加下载日志（专门用于下载相关日志）
        logger.add(
            config.get("Logging","download_log"),
            rotation=config.get("Logging","rotation"),
            retention=config.get("Logging","retention"),
            level=config.get("Logging","level"),
            format=config.get("Logging","format"),
            filter=lambda record: record["extra"].get("category") == "download"
        )

    @staticmethod
    def get_logger(category="business"):
        """
        获取日志对象
        :param category: "business" 业务日志 / "download" 下载日志 / "database" 数据库日志
        :return: 日志对象
        """
        return logger.bind(category=category)

    def update_config(self, new_config):
        """动态更新日志配置"""
        with self._lock:
            self._init_logger(new_config)

# ========== 示例使用 ==========
if __name__ == "__main__":
    log_service = LoggerService()

    # 业务日志
    business_logger = log_service.get_logger("business")
    business_logger.info("This is a business log entry.")

    # 下载日志
    download_logger = log_service.get_logger("download")
    download_logger.info("This is a download log entry.")

