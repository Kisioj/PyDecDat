from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTableView

app = QApplication([])
window = QWidget()

# standard item model
model = QStandardItemModel(5, 3)
model.setHorizontalHeaderLabels(['ID', 'DATE', 'VALUE'])
for row, text in enumerate(['Cell', 'Fish', 'Apple', 'Ananas', 'Mango']*20000):
    item = QStandardItem(text)
    model.setItem(row, 2, item)

# filter proxy model
filter_proxy_model = QSortFilterProxyModel()
filter_proxy_model.setSourceModel(model)
filter_proxy_model.setFilterKeyColumn(2) # third column

# line edit for filtering
layout = QVBoxLayout(window)
line_edit = QLineEdit()
line_edit.textChanged.connect(filter_proxy_model.setFilterRegExp)
layout.addWidget(line_edit)

# table view
table = QTableView()
table.setModel(filter_proxy_model)
layout.addWidget(table)

window.show()
app.exec_()