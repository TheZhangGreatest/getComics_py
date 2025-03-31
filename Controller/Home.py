from PyQt5.QtWidgets import QWidget, QHeaderView
from View.Ui_Home import Ui_Home
from Service.WebsiteService import WebsiteService
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from View.Delegate.CenteredCheckBoxDelegate import CenteredCheckBoxDelegate
from Config import Config
from PyQt5.QtCore import pyqtSignal
from Entity.ChapterTask import ChapterTask
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
        self.ui.checkAllBox.stateChanged.connect(self.checkAllBoxStateChanged)
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

        self.tableModel.setColumnCount(2)  # 两列：复选框 + 一列数据

        self.ui.tableView.setColumnWidth(0, 50)  # 第一列固定 50px，保持正方形
        self.ui.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 第一列固定大小
        self.ui.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ui.tableView.setItemDelegateForColumn(0, CenteredCheckBoxDelegate())
        self.ui.tableView.setAlternatingRowColors(True)  # 设置交替行颜色
        self.tableModel.itemChanged.connect(self.tableItemChanged)

    def searchButtonClicked(self):
        # 使用搜索内容发送
        self.websitesevice.search(self.ui.searchInput.text())
        
    def checkAllBoxStateChanged(self):
        check_state = self.ui.checkAllBox.checkState()
        self.tableModel.blockSignals(True)
        for i in range(self.tableModel.rowCount()):
            self.tableModel.item(i, 0).setCheckState(check_state)
        self.tableModel.blockSignals(False)
        self.ui.tableView.viewport().update()

    def downloadButtonClicked(self):
        chapters = []
        for i in range(self.tableModel.rowCount()):
            if self.tableModel.item(i, 0).checkState() == Qt.Checked:
                chapters.append(self.tableModel.item(i, 1).text())
        self.websitesevice.add_chapter_download_record(chapters)

    
    def comboBoxIndexChanged(self):
        self.websitesevice.set_active_website(self.ui.comboBox.currentText())

    def resultListClicked(self,index):
        selected_text = index.data()  # 获取选中行的文本
        self.websitesevice.get_chapter_list(selected_text)
    
    def tableItemChanged(self, item):
        if item.column() == 0:  # 只关心勾选框列
            checked_count = 0
            for i in range(self.tableModel.rowCount()):
                if self.tableModel.item(i, 0).checkState() == Qt.Checked:
                    checked_count += 1

            if checked_count == self.tableModel.rowCount() and self.tableModel.rowCount() > 0:
                # 全选上了，勾上全选框
                self.ui.checkAllBox.blockSignals(True)
                self.ui.checkAllBox.setCheckState(Qt.Checked)
                self.ui.checkAllBox.blockSignals(False)
            else:
                # 有取消选择，去掉全选框
                self.ui.checkAllBox.blockSignals(True)
                self.ui.checkAllBox.setCheckState(Qt.Unchecked)
                self.ui.checkAllBox.blockSignals(False)
    def updateResultList(self,result):
        self.resultListMoel.clear()
        for item in result:
            self.resultListMoel.appendRow(QStandardItem(item))
    def updateTableModel(self,result):
        self.tableModel.clear()
        for item in result:
            """添加一行数据"""
            check_item = QStandardItem()
            check_item.setCheckState(Qt.Unchecked)
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # 让复选框可用但不能编辑文本
            name_item = QStandardItem(item)  # 姓名
            self.tableModel.appendRow([check_item, name_item]) 
        self.ui.tableView.setColumnWidth(0, 50)  # 第一列固定 50px，保持正方形
        self.ui.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 第一列固定大小
        self.ui.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    def add_chapter_download_record_finished(self,chapter):
        self.add_chapter_download_record.emit(chapter)






