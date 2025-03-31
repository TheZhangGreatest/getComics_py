from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from Service.LoggerService import LoggerService
import traceback
from queue import Queue
import threading
from Config import Config

class ThreadPoolManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.max_threads = int(self.config.get("App", "thread_count",5))  # 最大线程数
        self.threads = []  # 线程列表
        self.task_queue = Queue()
        self.lock = threading.Lock()  # 线程锁，确保线程安全
    def start(self):
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            self.threads.append(t)
    def worker(self):
        while True:
            with self.lock:
                if self.max_threads > int(self.config.get("App", "thread_count",5)):
                    self.max_threads -= 1  # 减少线程数
                    self.threads.remove(threading.current_thread())
                    break
            task = self.task_queue.get()
            task.run()  # 执行任务
            self.task_queue.task_done()  # 标记任务完成
    def add_task(self, task):
        """添加任务到线程池"""
        self.task_queue.put(task)  # 将任务放入队列
class Task(QRunnable):
    def __init__(self, task_func,*args, **kwargs):
        super().__init__()
        self.task_func = task_func  # 任务函数
        self.args = args  # 函数参数
        self.kwargs = kwargs  # 函数关键字参数
        self.result = None  # 任务结果

    def run(self):
        self.result = self.task_func(*self.args, **self.kwargs)  # 执行任务

class DownloadTask(Task):
    """下载任务类"""
    def __init__(self, task_func,*args, **kwargs):
        super().__init__(task_func,*args, **kwargs)
        self.task_type = "DownloadTask"  # 任务类型
        self.logger = LoggerService().get_logger("download")  # 获取下载任务的日志记录器
        self.logger.info(f"DownloadTask initialized with args: {args}, kwargs: {kwargs}")
    def run(self):
        try:
            self.logger.info(f"Running DownloadTask with args: {self.args}, kwargs: {self.kwargs}")
            super().run()
            self.logger.info("DownloadTask finished")
        except Exception as e:
            self.logger.exception("Error in DownloadTask")
            traceback.print_exc()
class BussinessTask(Task):
    """业务逻辑任务类"""
    def __init__(self, task_func,*args, **kwargs):
        super().__init__(task_func,*args, **kwargs)
        self.task_type = "BusinessTask"  # 任务类型
        self.logger = LoggerService().get_logger("business")  # 获取业务逻辑任务的日志记录器
        self.logger.info(f"BusinessTask initialized with args: {args}, kwargs: {kwargs}")
        self.siganl = pyqtSignal(object)  # 定义信号，用于任务完成后发送结果
    def run(self):
        try:
            self.logger.info(f"Running BusinessTask with args: {self.args}, kwargs: {self.kwargs}")
            super().run()
            self.siganl.emit(self.result)  # 任务完成后发送信号
            self.logger.info("BusinessTask result: ", self.result)
        except Exception as e:
            self.logger.exception("Error in BusinessTask")
            traceback.print_exc()
