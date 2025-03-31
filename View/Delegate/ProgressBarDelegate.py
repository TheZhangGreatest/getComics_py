from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyleOptionProgressBar
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtGui import QLinearGradient, QBrush
from PyQt5.QtCore import QRect

class ProgressBarDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    def paint(self, painter, option, index):
        progress = int(float(index.model().data(index, Qt.DisplayRole)))

        # 2. 画霓虹边框（赛博朋克风）
        painter.save()
        pen = QPen(QColor("#00FFFF"))  # 青色霓虹
        pen.setWidth(4)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 180))  # 半透明黑色背景
        painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 5, 5)
        painter.restore()

        # 3. 画进度块（发光霓虹色）
        chunk_rect = option.rect.adjusted(4, 4, -4, -4)
        filled_width = int((progress / 100) * chunk_rect.width())
        chunk_filled = chunk_rect.adjusted(0, 0, -(chunk_rect.width() - filled_width), 0)

        if progress > 0:
            painter.save()
            gradient = QLinearGradient(chunk_filled.topLeft(), chunk_filled.topRight())
            gradient.setColorAt(0, QColor("#FF00FF"))  # 紫色
            gradient.setColorAt(1, QColor("#00FFFF"))  # 青色
            painter.setBrush(QBrush(gradient))
            
            pen = QPen(QColor("#FFFFFF"))  # 白色发光边框
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRoundedRect(chunk_filled, 5, 5)
            painter.restore()

        # 4. 绘制未来感 HUD 风格进度条（去掉系统默认绘制，改成自定义）
        painter.save()
        text_color = QColor("#00FFFF")  # 青色字体
        painter.setPen(text_color)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        text = f"{progress}%"
        painter.drawText(option.rect, Qt.AlignCenter, text)
        painter.restore()