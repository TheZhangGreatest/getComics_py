from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QStandardItem
class MultiFilterProxyModel(QSortFilterProxyModel):
    """
    通用型多字段筛选代理模型
    支持按多个列（字段）筛选，字段与条件为精确匹配（可扩展正则）
    """
    def __init__(self, sourceModel,ColumnCount, parent=None):
        super().__init__(parent)
        sourceModel.setColumnCount(ColumnCount)
        self.setSourceModel(sourceModel)
        self.task_item_map = {}
        self.filters = {}
        

    def setFilter(self, column, value):
        """
        设置某一列的筛选条件
        :param column: 列索引
        :param value: 字段值，为空代表清除该字段过滤
        """
        if value:
            self.filters[column] = value
        else:
            self.filters.pop(column, None)
        self.invalidateFilter()

    def clearFilters(self):
        """清除所有过滤条件"""
        self.filters.clear()
        self.invalidateFilter()
    def clearFilter(self,column):
        """清除指定过滤条件"""
        self.filters.pop(column, None)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        for column, expected_value in self.filters.items():
            index = model.index(source_row, column, source_parent)
            data = str(model.data(index)).strip()
            # 支持大小写不敏感精确匹配
            if data.lower() != expected_value.lower():
                return False
        return True
    def setHeader(self,List):
        """设置表头"""
        self.sourceModel().setHorizontalHeaderLabels(List)  
    
    def appendRow(self, data:list[QStandardItem]):
        """添加一行数据"""
        self.sourceModel().appendRow(data)
        # 获取最后一个数据
        id = data[0].data(Qt.UserRole)
        self.task_item_map[id] = data[0]

    def updateRow(self, id, data:list[QStandardItem]):
        """更新一行数据"""
        # 获取行号
        item = self.task_item_map.get(id)
        if item:
            row = item.row()
            # 更新数据
            for i in range(2,len(data)):
                # 更新数据
                self.sourceModel().setItem(row, i, data[i])

            # 发出 dataChanged 信号，刷新视图
            top_left = self.sourceModel().index(row, 0)
            bottom_right = self.sourceModel().index(row, len(data) - 1)
            self.sourceModel().dataChanged.emit(top_left, bottom_right)



    def removeRow(self, ids:list[int]):
        """删除多行数据"""
        if not ids:
            return
        ids.reverse()
        # 逆序删除，防止行索引变动
        for id in ids:
            # 获取行号
            item = self.task_item_map.get(id)
            if item:
                row = item.row()
                # 获取原始行号
                self.sourceModel().removeRow(row)  # 删除源模型中的行
                del self.task_item_map[id]  # 删除映射关系
