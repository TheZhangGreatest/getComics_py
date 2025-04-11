from PyQt5.QtWidgets import QWidget, QHeaderView
from View.Ui_Home import Ui_Home
from Service.WebsiteService import WebsiteService
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from View.Delegate.CenteredCheckBoxDelegate import CenteredCheckBoxDelegate
from Config import Config
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
class Home(QWidget):
    add_chapter_download_record = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.ui = Ui_Home()
        self.ui.setupUi(self)

        self.websitesevice = WebsiteService()
        websiteList = self.websitesevice.get_website_list()
        # 为下拉框添加选项
        for website in websiteList:
            self.ui.comboBox.addItem(website)
        self.websitesevice.set_active_website(self.ui.comboBox.currentText())

        # 绑定事件
        self.ui.searchButton.clicked.connect(self.searchButtonClicked)
        self.ui.downloadButton.clicked.connect(self.downloadButtonClicked)
        self.ui.comboBox.currentIndexChanged.connect(self.comboBoxIndexChanged)
        self.ui.resultList.clicked.connect(self.resultListClicked)
        self.websitesevice.searchFinished.connect(self.updateResultList)
        self.websitesevice.getChapterListFinished.connect(self.updateTableModel)
        self.websitesevice.addChapterDownloadRecordFinished.connect(self.add_chapter_download_record_finished)

        # 绑定数据
        self.resultListMoel = QStandardItemModel()
        self.ui.resultList.setModel(self.resultListMoel)

        self.tableModel = QStandardItemModel()
        self.ui.tableView.setModel(self.tableModel)
        self.tableModel.setColumnCount(1)  #一列数据
        self.ui.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.tableView.setAlternatingRowColors(True)  # 设置交替行颜色

        # 添加快捷键
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self.select_all_rows)
    def select_all_rows(self):
        """全选"""
        self.ui.tableView.selectAll()

    def searchButtonClicked(self):
        # 使用搜索内容发送
        self.websitesevice.search(self.ui.searchInput.text())
    

    def downloadButtonClicked(self):
        rows = self.ui.tableView.selectionModel().selectedRows()
        chapters = []
        for row in rows:
            chapters.append(self.tableModel.data(self.tableModel.index(row.row(), 0), Qt.DisplayRole))
        self.websitesevice.add_chapter_download_record(chapters)

    
    def comboBoxIndexChanged(self):
        self.websitesevice.set_active_website(self.ui.comboBox.currentText())

    def resultListClicked(self,index):
        selected_text = index.data()  # 获取选中行的文本
        self.websitesevice.get_chapter_list(selected_text)
    
    def updateResultList(self,result):
        self.resultListMoel.clear()
        for item in result:
            self.resultListMoel.appendRow(QStandardItem(item))
    def updateTableModel(self,result):
        self.tableModel.clear()
        for item in result:
            name_item = QStandardItem(item)  # 姓名
            self.tableModel.appendRow([name_item]) 
        self.ui.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    def add_chapter_download_record_finished(self,chapter):
        self.add_chapter_download_record.emit(chapter)






