from PyQt5.QtWidgets import QMainWindow
from View.Ui_Mainwindow import Ui_MainWindow
class Mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.home.add_chapter_download_record.connect(self.ui.download.add_chapter_download_record)




