from Controller import Mainwindow
from PyQt5.QtWidgets import QApplication
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow.Mainwindow()
    mainwindow.show()
    sys.exit(app.exec_())
