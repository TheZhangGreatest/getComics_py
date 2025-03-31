from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionButton, QStyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen


class CenteredCheckBoxDelegate(QStyledItemDelegate):
    """ 自定义代理，使复选框在单元格中居中，并且点击不变输入框 """

    def __init__(self, parent=None):
        super().__init__(parent) 
    def paint(self, painter, option, index):
        painter.fillRect(option.rect, Qt.GlobalColor.white)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        checkBoxOption = QStyleOptionButton()
        checkBoxOption.rect = option.rect
        checkState = index.data(Qt.ItemDataRole.CheckStateRole)
        if checkState == Qt.CheckState.Checked:
            checkBoxOption.state = QStyle.State(QStyle.StateFlag.State_On | QStyle.StateFlag.State_Enabled)
        else:
            checkBoxOption.state = QStyle.State(QStyle.StateFlag.State_Off | QStyle.StateFlag.State_Enabled)
            
        checkBoxSize = QApplication.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
        offset = (option.rect.width() - checkBoxSize) // 2
        checkBoxOption.rect.setX(option.rect.x() + offset)
        QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, checkBoxOption, painter)


    def editorEvent(self, event, model, option, index):
        """ 处理鼠标点击事件"""
        if event.type() == event.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            new_state = Qt.Checked if index.data(Qt.CheckStateRole) == Qt.Unchecked else Qt.Unchecked
            model.setData(index, new_state, Qt.CheckStateRole)
            return True
        return False


# app = QApplication([])

# # 创建表格
# table = QTableWidget(5, 3)
# table.setWindowTitle("美观的居中复选框代理")
# table.setFixedSize(400, 250)

# # 设置复选框代理
# delegate = CenteredCheckBoxDelegate()
# table.setItemDelegateForColumn(1, delegate)

# # 添加数据
# for row in range(5):
#     for col in range(3):
#         item = QTableWidgetItem()
#         if col == 1:  # 只在第 2 列放置复选框
#             item.setCheckState(Qt.Unchecked)
#             item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # 让复选框可用但不能编辑文本
#         table.setItem(row, col, item)

# table.show()
# app.exec_()