from Config import Config
from Mapper.ChapterTaskMapper import ChapterTaskMapper
from Mapper.ImageTaskMapper import ImageTaskMapper
import threading
from PyQt5.QtCore import pyqtSignal
from Enum.DownloadStatus import DownloadStatus
import requests
import os
from PIL import Image
import zipfile
from collections import defaultdict
from Entity.ImageTask import ImageTask
from Entity.ChapterTask import ChapterTask
from PyQt5.QtCore import QObject
from Service.Database import Database
from Service.ThreadService import ThreadPoolManager, DownloadTask
from Service.LoggerService import LoggerService
class DownloadService(QObject):
    update_chapter_task = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chapterTaskMapper = ChapterTaskMapper()
        self.imageTaskMapper = ImageTaskMapper()
        self.chapters = {task.id: task for task in self.chapterTaskMapper.list_not_success()}
        self.config = Config()
        self.chapter_locks = defaultdict(threading.Lock)
        self.logger = LoggerService().get_logger("download")
        self.db = Database()
        # 记录当前在队列里面的任务，避免重复添加
        self.task_set = set()
        # 线程池管理器
        self.thread_pool = ThreadPoolManager.instance(self)
        for chapter in self.chapters.values():
            if chapter.status == DownloadStatus.DOWNLOADING:
                self.put_task(self.imageTaskMapper.list_by_chapter_id(chapter.id))
    def start(self):
        """启动下载服务"""
        self.thread_pool.start()
    # 将任务列表加入线程池
    def put_task(self, tasks: list[ImageTask]):
        for task in tasks:
            # 过滤掉已经完成的任务，以及已经在队列中的任务
            if task.id not in self.task_set and task.status == DownloadStatus.DOWNLOADING:
                self.task_set.add(task.id)
                self.thread_pool.add_task(task.image_index,DownloadTask(self.downloadImage,task))
    def downloadImage(self,task: ImageTask = None):
        self.task_set.remove(task.id)  # 从任务集合中移除
        """工作线程，处理任务队列中的任务"""
        # 下载图片,会有四种返回值，但是只处理两种，删除和暂停不处理
        with self.get_chapter_lock(task.chapter_id):
            # 防止章节任务被其他线程删除
            if task.chapter_id not in self.chapters:
                return
            chapter = self.chapters.get(task.chapter_id)
            # 防止已经失败或者暂停的任务被下载
            if chapter.status != DownloadStatus.DOWNLOADING:
                return
        result = self.download(task)
        if result:
            self.download_success(task, chapter)
        else:
            self.logger.error(f"Download failed for {task.image_url}")
            self.download_failed(task, chapter)
    def download(self, task: ImageTask):
        try:
            response = requests.get(task.image_url, timeout=10)
            content_type = response.headers.get('Content-Type', '')
            ext = { 'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp' }.get(content_type, '.jpg')
            os.makedirs(os.path.normpath(task.file_path), exist_ok=True)
            image_path = os.path.join(os.path.normpath(task.file_path), f"{int(task.image_index):03d}{ext}")
            with self.get_chapter_lock(task.chapter_id):
                # 防止章节任务被其他线程删除
                if task.chapter_id not in self.chapters:
                    return False
                chapter = self.chapters.get(task.chapter_id)
                # 防止已经失败或者暂停的任务被下载
                if chapter.status != DownloadStatus.DOWNLOADING:
                    return False
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return True
        except requests.RequestException as e:
            self.logger.error(f"Network error in download {task.image_url}: {e}")
            return False
        except OSError as e:
            self.logger.error(f"File error in download {task.image_url}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error in download {task.image_url}: {e}")
            return False
    def download_failed(self, task: ImageTask, chapter: ChapterTask):
        """下载失败，添加重试机制"""
        if task.retry_count < int(self.config.get('App', 'max_retry', 3)):
            task.retry_count += 1
            self.put_task([task])
            self.logger.info(f"Retrying download for {task.image_url}, attempt {task.retry_count}")
        else:
            with self.get_chapter_lock(chapter.id):
                if chapter.id in self.chapters:
                    chapter.status = DownloadStatus.FAILED
                    self.chapterTaskMapper.update_task(chapter)
                    self.update_chapter_task.emit(chapter)
    def download_success(self, task: ImageTask, chapter: ChapterTask):
        """下载成功，更新任务状态"""
        # 更新章节任务状态
        with self.db.connect() as conn:  # 确保在同一事务中
            with self.get_chapter_lock(chapter.id):
                if chapter.id in self.chapters:
                    chapter.downloaded_images += 1
                    self.logger.info(f"Downloaded {chapter.downloaded_images}/{chapter.total_images} images for {chapter.chapter_title}")
                    # 判断是否下载完成
                    if chapter.downloaded_images == chapter.total_images:
                        self.generate_comic_format(chapter)
                        chapter.status = DownloadStatus.SUCCESS
                        #删除任务
                        del self.chapters[chapter.id]
                        self.logger.info(f"Download completed for {chapter.chapter_title}")
                    self.chapterTaskMapper.update_task(chapter,conn)
                    self.update_chapter_task.emit(chapter)
            # 更新图片任务状态
            task.status = DownloadStatus.SUCCESS
            self.imageTaskMapper.update_task(task,conn)
        
    def generate_comic_format(self, chapter: ChapterTask):
        images_path = os.path.join(os.path.normpath(chapter.save_path), chapter.chapter_title)
        if chapter.save_format == "cbz":
            self.generate_comic_cbz(images_path, f"{images_path}.cbz")
        elif chapter.save_format == "pdf":
            self.generate_comic_pdf(images_path, f"{images_path}.pdf")
        if self.config.get('App', 'keep_original', 'false') == 'false':
            for img in os.listdir(images_path):
                os.remove(os.path.join(images_path, img))
            os.rmdir(images_path)
            

    def generate_comic_pdf(self, folder_path, output_pdf_path):
        image_files = sorted(
            [os.path.join(os.path.normpath(folder_path), f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        )
        if not image_files:
            print("No image files found")
            return

        images = [Image.open(img_path).convert('RGB') for img_path in image_files]
        first_img = images.pop(0)
        first_img.save(output_pdf_path, save_all=True, append_images=images, quality=95)
        print(f"Comic PDF generated: {output_pdf_path}")

    def generate_comic_cbz(self, folder_path, output_cbz_path):
        image_files = sorted(
            [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        )
        if not image_files:
            print("No image files found")
            return

        with zipfile.ZipFile(output_cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for img_path in image_files:
                img_name = os.path.basename(img_path)
                cbz.write(img_path, arcname=img_name)
        print(f"Comic CBZ generated: {output_cbz_path}")

    def pause_chapter_task(self, chapter_ids: list[int]):
        for chapter_id in chapter_ids:
            with self.get_chapter_lock(chapter_id):
                if chapter_id in self.chapters:
                    self.chapters[chapter_id].status = DownloadStatus.PAUSED
                    self.chapterTaskMapper.update_task(self.chapters[chapter_id])
                    self.update_chapter_task.emit(self.chapters[chapter_id])

    def resume_chapter_task(self, chapter_ids: list[int]):
        for chapter_id in chapter_ids:
            with self.get_chapter_lock(chapter_id):
                if chapter_id in self.chapters:
                    self.chapters[chapter_id].status = DownloadStatus.DOWNLOADING
                    self.chapterTaskMapper.update_task(self.chapters[chapter_id])
                    self.put_task(self.imageTaskMapper.list_by_chapter_id(chapter_id))
                    self.update_chapter_task.emit(self.chapters[chapter_id])
            


    def get_chapter_lock(self, chapter_id):
        return self.chapter_locks[chapter_id]
    
    def add_chapter_task(self, chapter: ChapterTask):
        """添加章节下载任务，直接更新任务队列"""
        with self.get_chapter_lock(chapter.id):
            # 更新章节信息
            self.chapters[chapter.id] = chapter
            # 添加图片任务
            self.put_task(self.imageTaskMapper.list_by_chapter_id(chapter.id))

    def delete_chapter_task(self, chapter_ids: list[int]):
        """删除章节任务"""
        for chapter_id in chapter_ids:
            with self.get_chapter_lock(chapter_id):
                if chapter_id in self.chapters:
                    # 删除章节信息
                    del self.chapters[chapter_id]
    

