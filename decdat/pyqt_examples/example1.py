#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QGridLayout()
        self.setLayout(layout)

        model = QDirModel()

        self.columnview = QColumnView()
        self.columnview.setModel(model)
        layout.addWidget(self.columnview)

app = QApplication(sys.argv)

screen = Window()
screen.show()

sys.exit(app.exec_())