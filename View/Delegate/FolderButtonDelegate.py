from PyQt5.QtWidgets import QApplication, QTableView, QStyledItemDelegate
from PyQt5.QtWidgets import QStyle
from PyQt5.QtCore import QModelIndex, Qt, QRect, QAbstractItemModel, QEvent
from PyQt5.QtGui import QPainter, QIcon, QBrush, QColor
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QStyleOptionViewItem

import os
import sys

class FolderButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_icon = QApplication.style().standardIcon(QStyle.SP_DirIcon)
        self.hovered = False  # 用于判断鼠标是否悬停在图标上

    def paint(self, painter, option, index):
        """ 绘制文件夹按钮 """
        painter.save()

        # 获取单元格的矩形区域
        rect = option.rect
        icon_size = min(rect.height(), 20)
        button_rect = QRect(
            rect.center().x() - icon_size // 2,
            rect.center().y() - icon_size // 2,
            icon_size,
            icon_size
        )
        # 设置悬停效果（改变颜色或图标）
        if self.hovered:
            painter.setBrush(QBrush(QColor(200, 200, 255)))  # 悬停时背景颜色
        else:
            painter.setBrush(QBrush(Qt.transparent))  # 默认背景透明
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(button_rect, 5, 5)

        # 绘制文件夹图标
        if not self.folder_icon.isNull():
            self.folder_icon.paint(painter, button_rect)

        painter.restore()

    def editorEvent(self, event, model, option, index):
        self.hovered = False
        if event.type() == event.MouseMove:  # 鼠标进入
            if self.isButtonContains(event, option):
                self.hovered = True
            return True
        elif event.type() == event.MouseButtonPress:  # 鼠标点击
            if self.isButtonContains(event, option):
                folder_path = os.path.abspath(index.data(Qt.DisplayRole))
                if os.path.exists(folder_path):
                    os.startfile(folder_path)  # 打开文件夹
            return True
        return False
    def isButtonContains(self, event, option):
        mouser_pos = event.pos()
        """ 处理鼠标点击事件 """
        rect = option.rect
        icon_size = min(rect.height(), 20)
        button_rect = QRect(
            rect.center().x() - icon_size // 2,
            rect.center().y() - icon_size // 2,
            icon_size,
            icon_size
        )
        return button_rect.contains(mouser_pos)