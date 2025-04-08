from Controller import Mainwindow
from PyQt5.QtWidgets import QApplication
import os
os.add_dll_directory("D:/soft/msys64/ucrt64/bin")
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow.Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())

