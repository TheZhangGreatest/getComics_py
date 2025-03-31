from PyQt5.QtCore import QObject, pyqtSignal
from Service.Website.WebsiteFactory import WebsiteFactory
from Service.ThreadService import ThreadPoolManager, BussinessTask
from PyQt5.QtCore import Qt
class WebsiteService(QObject):
    searchFinished = pyqtSignal(list)
    getChapterListFinished = pyqtSignal(list)
    addChapterDownloadRecordFinished = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = ThreadPoolManager.instance(self)  # 线程池管理器
        self.active_website = None  # 默认没有网站实例
        self.website_factory = WebsiteFactory()
        self.thread_pool.start()  # 启动线程池
        
        

    def get_website_list(self):
        return self.website_factory.list_websites()
    def set_active_website(self,website_name):
        if self.active_website:
            self.active_website.addChapterDownloadRecordFinished.disconnect(self.add_chapter_download_record_finished)
        # 设置当前活动网站
        self.active_website = self.website_factory.get_website(website_name)
        self.active_website.addChapterDownloadRecordFinished.connect(self.add_chapter_download_record_finished,Qt.QueuedConnection)

    
    def search(self, searchContent):
        """启动搜索操作"""
        task = BussinessTask(self.active_website.search,  searchContent)
        task.set_signal(self.searchFinished)
        self.thread_pool.add_task(-5,task)  # 添加任务到线程池

    def get_chapter_list(self, comic_name):
        """启动获取章节列表操作"""
        task = BussinessTask(self.active_website.get_chapter_list, comic_name)
        task.set_signal(self.getChapterListFinished)
        self.thread_pool.add_task(-4,task)

    def add_chapter_download_record(self, chapters):
        """启动添加章节下载记录操作"""
        task = BussinessTask(self.active_website.add_chapter_download_record, chapters)
        self.thread_pool.add_task(0,task)
    def add_chapter_download_record_finished(self, chapter):
        """添加章节下载记录完成"""
        self.addChapterDownloadRecordFinished.emit(chapter)
    


    

