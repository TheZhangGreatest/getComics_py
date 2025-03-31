from PyQt5.QtCore import QObject, pyqtSignal
from Service.Website.WebsiteFactory import WebsiteFactory
from PyQt5.QtCore import QThreadPool, QRunnable
from loguru import logger
class Worker(QRunnable):
    def __init__(self, func, signal, *args):
        super().__init__()
        self.func = func
        self.signal = signal
        self.args = args

    def run(self):
        result = self.func(*self.args)
        self.signal.emit(result)
class WebsiteService(QObject):
    searchFinished = pyqtSignal(list)
    getChapterListFinished = pyqtSignal(list)
    addChapterDownloadRecordFinished = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()  # 获取全局线程池
        self.active_website = None  # 默认没有网站实例
        self.website_factory = WebsiteFactory()

    def get_website_list(self):
        return self.website_factory.list_websites()
    def set_active_website(self,website_name):
        self.active_website = self.website_factory.get_website(website_name)
    def search(self, searchContent):
        """启动搜索操作"""
        task = Worker(self.active_website.search, self.searchFinished, searchContent)
        self.thread_pool.start(task)

    def get_chapter_list(self, comic_name):
        """启动获取章节列表操作"""
        task = Worker(self.active_website.get_chapter_list, self.getChapterListFinished, comic_name)
        self.thread_pool.start(task)

    def add_chapter_download_record(self, chapters):
        """启动添加章节下载记录操作"""
        task = Worker(self.active_website.add_chapter_download_record, self.addChapterDownloadRecordFinished, chapters)
        self.thread_pool.start(task)
    


    

