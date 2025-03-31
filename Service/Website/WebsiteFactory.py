import importlib
import os
import pkgutil
import inspect
from Config import Config
from Service.Website.BaseWebsite import BaseWebsite
# 网站工厂类，根据配置文件返回对应的网站实例
class WebsiteFactory:
    """网站工厂类，根据配置文件返回对应的网站实例"""
    def __init__(self):
        """初始化方法，确保只执行一次"""
        self.websiteList = {}
        self.config = Config()
        self.website_dir = self.config.get("App", "website_dir")
        self.load_websites()
        

    def load_websites(self):
        """从插件目录动态加载所有类"""
        if not os.path.exists(self.website_dir):
            print(f"网站插件目录 {self.website_dir} 不存在！")
            return

        for _, module_name, _ in pkgutil.iter_modules([self.website_dir]):
            module_path = f"Ext.{module_name}"  # 形成完整模块路径
            try:
                module = importlib.import_module(module_path)  # 动态导入模块
                for name, obj in inspect.getmembers(module, inspect.isclass):  # 获取模块中的所有类
                    self.websiteList[name] = obj  # 直接存类引用
                    print(f"加载插件: {name} -> {module_path}")
            except Exception as e:
                print(f"加载 {module_name} 失败: {e}")
#返回值类型是BaseWebsite
    def get_website(self, class_name, *args, **kwargs)->BaseWebsite:
        """按类名返回网站实例"""
        if class_name not in self.websiteList:
            print(f"类 {class_name} 未找到！")
            return None
        return self.websiteList[class_name](*args, **kwargs)  # 实例化插件类

    def list_websites(self):
        """返回所有加载的类名"""
        return list(self.websiteList.keys())
