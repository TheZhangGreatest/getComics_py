from Config import Config
from PyQt5.QtWidgets import QWidget
from View.Ui_Download import Ui_Download
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from PyQt5.QtCore import Qt
from View.Delegate.ProgressBarDelegate import ProgressBarDelegate
from View.Delegate.FolderButtonDelegate import FolderButtonDelegate
from Mapper.ChapterTaskMapper import ChapterTaskMapper
from PyQt5.QtWidgets import QShortcut
from Model.MultiFilterProxyModel import MultiFilterProxyModel
from Enum.DownloadStatus import DownloadStatus
from Entity.ChapterTask import ChapterTask
from Service.DownloadService import DownloadService
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMessageBox
STATUS_MAP = {
    DownloadStatus.PAUSED: "暂停",
    DownloadStatus.DOWNLOADING: "下载中",
    DownloadStatus.SUCCESS: "下载完成",
    DownloadStatus.FAILED: "下载失败"
}
class Download(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.ui = Ui_Download()
        self.ui.setupUi(self)
        self.comic = {}

        # 绑定GUI事件
        self.ui.statusComboBox.currentIndexChanged.connect(self.statusComboBoxIndexChanged)
        self.ui.comicComboBox.currentIndexChanged.connect(self.comicComboBoxIndexChanged)
        self.ui.chapterComboBox.currentIndexChanged.connect(self.chapterComboBoxIndexChanged)
        self.ui.deleteButton.clicked.connect(self.deleteButtonClicked)
        self.ui.dwonloadButton.clicked.connect(self.downloadButtonClicked)
        self.ui.pauseButton.clicked.connect(self.pauseButtonClicked)


        # 绑定数据
        self.tableModel = MultiFilterProxyModel(QStandardItemModel(self),6,self) #漫画名，章节名，下载进度，下载状态，下载地址，更新时间
        self.tableModel.setHeader(["漫画", "章节", "进度", "状态", "地址", "更新时间"])
        self.ui.tableView.setModel(self.tableModel)
        self.ui.tableView.setItemDelegateForColumn(2, ProgressBarDelegate(self))
        self.ui.tableView.setItemDelegateForColumn(4, FolderButtonDelegate(self))
        self.ui.tableView.setAlternatingRowColors(True)  # 设置交替行颜色
        self.chapterTaskMapper = ChapterTaskMapper()
        for task in self.chapterTaskMapper.list_all():
            self.appendRow(task)

        # 设置表格列宽
        header = self.ui.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 漫画名根据内容调整
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 章节名根据内容调整
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 进度固定宽度
        self.ui.tableView.setColumnWidth(2, 150)  # 进度固定 150 像素
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 状态固定宽度
        self.ui.tableView.setColumnWidth(3, 80)  # 状态固定 80 像素
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 地址固定宽度
        self.ui.tableView.setColumnWidth(4, 40)  # 地址固定 40 像素
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 更新时间固定宽度
        self.ui.tableView.setColumnWidth(5, 165)  # 更新时间固定 165 像素

        header.setSectionsMovable(True)   # 允许拖动调整列顺序
        header.setStretchLastSection(True)  # 让最后一列填充剩余空间

        # 启动下载服务
        self.download_service = DownloadService(self)
        self.download_service.update_chapter_task.connect(self.updateRow,Qt.QueuedConnection)
        self.download_service.start()

        # 添加快捷键
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self.select_all_rows)
        # 记录漫画名和对应的章节名，用作下拉框筛选
        
    def deleteButtonClicked(self):
        rows = self.ui.tableView.selectionModel().selectedRows()
        ids = []
        for row in rows:
            id = self.tableModel.data(self.tableModel.index(row.row(), 0), Qt.UserRole)
            ids.append(id)
                # 确认删除
        if len(ids) == 0:
            return
        reply = QMessageBox.question(self, '确认删除', "你确定要删除选中的记录吗?", 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chapterTaskMapper.delete_by_id(ids)
            self.removeRow(ids)
            self.download_service.delete_chapter_task(ids)
        
    def updateRow(self, task : ChapterTask):
        self.tableModel.updateRow(task.id, [
            QStandardItem(task.comic_title),
            QStandardItem(task.chapter_title),
            QStandardItem(str(int(task.downloaded_images)*100/int(task.total_images))),
            QStandardItem(STATUS_MAP.get(task.status, "未知状态")),
            QStandardItem(task.save_path),
            QStandardItem(task.updated_at)
        ])
        
    def appendRow(self, task : ChapterTask):
        row = [
            QStandardItem(task.comic_title),
            QStandardItem(task.chapter_title),
            QStandardItem(str(int(task.downloaded_images)*100/int(task.total_images))),
            QStandardItem(STATUS_MAP.get(task.status, "未知状态")),
            QStandardItem(task.save_path),
            QStandardItem(task.updated_at)
        ]
        row[0].setData(task.id, Qt.UserRole)
        # 添加到表格模型
        self.tableModel.appendRow(row)
        # 添加到漫画列表
        if task.comic_title not in self.comic:
            self.comic[task.comic_title] = []
            self.ui.comicComboBox.addItem(task.comic_title)
        self.comic[task.comic_title].append(task.chapter_title)
    def removeRow(self, ids:list[int]):
        self.tableModel.removeRow(ids)

    def select_all_rows(self):
        self.ui.tableView.selectAll()
    def statusComboBoxIndexChanged(self):
        if(self.ui.statusComboBox.currentText() != '全部'):
            self.tableModel.setFilter(3,self.ui.statusComboBox.currentText())
        else:
            self.tableModel.clearFilter(3)
    def comicComboBoxIndexChanged(self):
        if(self.ui.comicComboBox.currentText() != '全部'):
            self.tableModel.setFilter(0,self.ui.comicComboBox.currentText())
            self.ui.chapterComboBox.clear()
            self.ui.chapterComboBox.addItem('全部')
            self.ui.chapterComboBox.addItems(self.comic[self.ui.comicComboBox.currentText()])
        else:
            self.ui.chapterComboBox.clear()
            self.ui.chapterComboBox.addItem('全部')
            self.tableModel.clearFilter(0)
    def chapterComboBoxIndexChanged(self):
        if(self.ui.chapterComboBox.currentText() != '全部'):
            self.tableModel.setFilter(1,self.ui.chapterComboBox.currentText())
        else:
            self.tableModel.clearFilter(1)

    def add_chapter_download_record(self, chapters: list):
        for chapter in chapters:
            self.appendRow(chapter)
            self.download_service.add_chapter_task(chapter)

    def downloadButtonClicked(self):
        rows = self.ui.tableView.selectionModel().selectedRows()
        ids = []
        for row in rows:
            id = self.tableModel.data(self.tableModel.index(row.row(), 0), Qt.UserRole)
            ids.append(id)
        if len(ids) == 0:
            return
        self.download_service.resume_chapter_task(ids)
    def pauseButtonClicked(self):
        rows = self.ui.tableView.selectionModel().selectedRows()
        ids = []
        for row in rows:
            id = self.tableModel.data(self.tableModel.index(row.row(), 0), Qt.UserRole)
            ids.append(id)
        if len(ids) == 0:
            return
        self.download_service.pause_chapter_task(ids)
