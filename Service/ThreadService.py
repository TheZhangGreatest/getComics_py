from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from Service.LoggerService import LoggerService
import traceback
import queue
import threading
from Config import Config

class ThreadPoolManager(QObject):
    _instance = None  # 类属性，用于存储唯一实例
    def __init__(self, parent=None):
        """初始化线程池管理器"""
        super().__init__(parent)
        self.lock = threading.Lock()  # 线程锁，确保线程安全
        self.config = Config()
        self.set_max_threads()  # 设置最大线程数
        self.threads = []  # 线程列表
        self.task_queue = queue.PriorityQueue()  # 使用优先级队列来管理任务
    @classmethod
    def instance(cls, parent=None):
        """获取唯一实例"""
        if cls._instance is None:
            cls._instance = ThreadPoolManager(parent)
        return cls._instance
    def start(self):
        with self.lock:
            while len(self.threads)< self.max_threads:
                """启动线程池"""
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
            _,task = self.task_queue.get()
            task.run()  # 执行任务
            self.task_queue.task_done()  # 标记任务完成
    def set_max_threads(self):
        """设置最大线程数"""
        with self.lock:
            self.max_threads = int(self.config.get("App", "thread_count", 5))  # 更新最大线程数
    def add_task(self, priority,task):
        """添加任务到线程池"""
        self.task_queue.put((priority,task)) # 将任务放入队列
class Task(QRunnable):
    def __init__(self, task_func,*args, **kwargs):
        super().__init__()
        self.task_func = task_func  # 任务函数
        self.args = args  # 函数参数
        self.kwargs = kwargs  # 函数关键字参数
        self.result = None  # 任务结果

    def run(self):
        self.result = self.task_func(*self.args, **self.kwargs)  # 执行任务
    def __lt__(self, other):
        return True

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
        self.siganl = None  # 定义信号，用于任务完成后发送结果
    def run(self):
        try:
            self.logger.info(f"Running BusinessTask with args: {self.args}, kwargs: {self.kwargs}")
            super().run()
            if self.siganl is not None:
                self.siganl.emit(self.result)
            self.logger.info("BusinessTask result: ", self.result)
        except Exception as e:
            self.logger.exception("Error in BusinessTask")
            traceback.print_exc()
    def set_signal(self, signal):
        """设置信号，用于任务完成后发送结果"""
        self.siganl = signal
