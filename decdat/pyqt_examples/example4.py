import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class MyFrame(QtWidgets.QFrame):
    def __init__(self, parent=None,initials=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.table = QtWidgets.QTableWidget(5,3,self)
        self.table.move(30,30)
        self.table.resize(400,300)

        item1 = QtWidgets.QTableWidgetItem('red')
        item1.setBackground(QtGui.QColor(255, 0, 0))
        self.table.setHorizontalHeaderItem(0,item1)

        item2 = QtWidgets.QTableWidgetItem('green')
        item2.setBackground(QtGui.QColor(0, 255, 0))
        self.table.setHorizontalHeaderItem(1,item2)

        item3 = QtWidgets.QTableWidgetItem('blue')
        item3.setBackground(QtGui.QColor(0, 0, 255))
        self.table.setHorizontalHeaderItem(2,item3)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion')) # won't work on windows style.
    Frame = MyFrame(None)
    Frame.resize(500,400)
    Frame.show()
    app.exec_()