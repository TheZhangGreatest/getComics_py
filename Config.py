from PyQt5.QtCore import QSettings
import os

class Config:
    _instance = None

    def __new__(cls, config_file='config.ini'):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init_config(config_file)
        return cls._instance

    def _init_config(self, config_file):
        self.config_file = config_file
        # 使用QSettings读取INI配置
        self.settings = QSettings(self.config_file, QSettings.IniFormat)

    def get(self, section, key, default=None):
        """读取配置"""
        return self.settings.value(f"{section}/{key}", default)

    def set(self, section, key, value):
        """写入配置"""
        self.settings.setValue(f"{section}/{key}", value)
        self.settings.sync()

    def all_keys(self):
        return self.settings.allKeys()
