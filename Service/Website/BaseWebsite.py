from abc import ABC, abstractmethod
from Service.NetworkService import NetworkService
from PyQt5.QtCore import pyqtSignal, QObject
from Mapper.ChapterTaskMapper import ChapterTaskMapper
from Mapper.ImageTaskMapper import ImageTaskMapper
from Entity.ImageTask import ImageTask
from Entity.ChapterTask import ChapterTask
from Config import Config
from Enum.DownloadStatus import DownloadStatus
from Service.DownloadService import DownloadService
# 网站基类，定义了搜索和下载方法，以及搜索结果解析方法
class BaseWebsite(QObject):
    addChapterDownloadRecordFinished = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = "base"
        self.cur_comic_name = ""
        self.cur_chapter_name = ""
        self.cur_chapter_pages_number = 0
        self.network_service = NetworkService()
        self.chapter_task_mapper = ChapterTaskMapper()
        self.image_task_mapper = ImageTaskMapper()
        self.config = Config()
        
        
    def search(self, searchContent):
        pass
    def get_chapter_list(self, name):
        pass
    def add_chapter_download_record(self, chapters):
        for name in chapters:
            self.get_chapter_pages_number(name)
            chapter = ChapterTask()
            chapter.comic_title = self.cur_comic_name
            chapter.chapter_title = name
            
            chapter.save_path = self.config.get("App","download_path")+"/"+self.name+"/"+self.cur_comic_name
            chapter.status = DownloadStatus.DOWNLOADING
            chapter.save_format = self.config.get("App","save_format")
            chapter.total_images = self.cur_chapter_pages_number
            chapter.downloaded_images = 0
            # 写入数据库
            chapter.id = self.chapter_task_mapper.insert(chapter)
            self.add_image_download_record(chapter.id, chapter.save_path+"/"+name)
            self.addChapterDownloadRecordFinished.emit(chapter)
        
    def add_image_download_record(self, chapter_id,output_path):
        image = ImageTask()
        image.chapter_id = chapter_id
        image.file_path = output_path
        image.status = DownloadStatus.DOWNLOADING
        for i in range(1, self.cur_chapter_pages_number+1):
            image.image_index = i
            #获取图片链接
            image.image_url = self.get_image_url(i)
            self.image_task_mapper.insert(image)

    def get_image_url(self, i):
        pass
    def get_chapter_pages_number(self, name):
        pass