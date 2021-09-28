import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextOption
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp, QFileDialog, \
    QVBoxLayout, QTableWidgetItem, QTableWidget, QWidget, QHBoxLayout, QPushButton, \
    QSplitter, QComboBox, QLineEdit, QTabWidget, QTextEdit, QAbstractItemView, QHeaderView, QFrame, \
    QStyleFactory


import decompiler
from dat import Dat
from decompiler import get_code, get_tokens
from dat_token import Token



class TableWidgetItemWithNumber(QTableWidgetItem):
    def __lt__(self, other):
        return int(self.text()) < int(other.text())


ROWS = [
    'id', 'sort_table_id', 'count', 'type', 'type_as_str', 'flags', 'flags_as_str', 'space', 'has_name',
    'name', 'offset', 'file_index',
    'line_start', 'line_count', 'char_start', 'char_count', ('address', 'class_offset', 'content'), 'parent_index',
]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbolsTable = None
        self.symbolDetails = None
        self.sourceCode = None
        self.assemblyCode = None
        self.dat = None
        self.decompiler = None
        self.initUI()

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QHBoxLayout()
        centralWidget.setLayout(layout)

        menuBar = self.menuBar()

        actionOpen = QAction('&Open', self)
        actionOpen.setShortcut('Ctrl+O')
        actionOpen.setStatusTip('Open .dat file')
        actionOpen.triggered.connect(self.selectDat)  # FIXME when only 1 result after searching, then it doesnt work, e.g.: b_validateother

        actionExit = QAction('&Exit', self)
        actionExit.setShortcut('Ctrl+Q')
        actionExit.setStatusTip('Exit application')
        actionExit.triggered.connect(qApp.quit)

        menuFile = menuBar.addMenu('&File')
        menuFile.addAction(actionOpen)
        menuFile.addSeparator()
        menuFile.addAction(actionExit)

        actionToSingleFile = QAction('&To single file', self)
        actionToSingleFile.triggered.connect(self.export_all)

        actionToMultipleFiles = QAction('&To multiple files ', self)
        actionToMultipleFiles.triggered.connect(qApp.quit)

        actionWithDefinition = QAction('&With export definition', self)
        actionWithDefinition.triggered.connect(qApp.quit)

        actionCurrentSymbol = QAction('&Only Current Symbol', self)
        actionCurrentSymbol.triggered.connect(qApp.quit)

        menuExport = menuBar.addMenu('&Export')
        menuExport.addAction(actionToSingleFile)
        menuExport.addAction(actionToMultipleFiles)
        menuExport.addAction(actionWithDefinition)
        menuExport.addSeparator()
        menuExport.addAction(actionCurrentSymbol)

        actionAbout = QAction('&About', self)
        actionAbout.triggered.connect(self.about)

        actionShowLog = QAction('&Show Log', self)
        actionShowLog.triggered.connect(qApp.quit)

        actionRegEx = QAction('&RegEx', self)
        actionRegEx.triggered.connect(qApp.quit)

        actionAssembly = QAction('&Assembly', self)
        actionAssembly.triggered.connect(qApp.quit)

        actionExportDefinition = QAction('&Export definition', self)
        actionExportDefinition.triggered.connect(qApp.quit)

        menuHelp = menuBar.addMenu('&Help')
        menuHelp.addAction(actionAbout)
        menuHelp.addAction(actionShowLog)
        menuHelp.addSeparator()
        menuHelp.addAction(actionRegEx)
        menuHelp.addAction(actionAssembly)
        menuHelp.addAction(actionExportDefinition)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet('QSplitter::handle {background: url("splitter.png"); height: 8px; width:8px;}')
        layout.addWidget(splitter)

        leftside = QWidget()
        leftsidelayout = QVBoxLayout()
        leftside.setLayout(leftsidelayout)


        rightsplitter = QSplitter(Qt.Vertical)
        splitter.addWidget(leftside)
        splitter.addWidget(rightsplitter)

        self.symbolsTable = self.createSymbolsTableWidget(parent=leftsidelayout)

        searchwidget = QWidget()
        searchlayout = QHBoxLayout()
        searchwidget.setLayout(searchlayout)

        cb = QComboBox()
        cb.addItems(["Id", "Symbol name", "Type"])
        self.searchInput = QLineEdit()
        pb = QPushButton("Search")
        self.searchInput.returnPressed.connect(self.search)

        searchlayout.addWidget(cb)
        searchlayout.addWidget(self.searchInput)
        searchlayout.addWidget(pb)

        leftsidelayout.addWidget(searchwidget)

        tabs = QTabWidget()
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        tabs.setFont(font)

        tab1 = QTextEdit()
        tab1.setWordWrapMode(QTextOption.NoWrap)
        tab1.setStyleSheet("QTextEdit { margin: 5px; border: 1px solid lightgrey}")
        # tab1.setFrameStyle(QFrame.NoFrame)
        font = QFont()
        font.setPointSize(12)
        font.setFamily("Courier New")
        tab1.setFont(font)

        tab2 = QTextEdit()
        tab2.setStyleSheet("QTextEdit { margin: 5px; border: 1px solid lightgrey}")
        tab2.setFrameStyle(QFrame.NoFrame)
        tab2.setFont(font)

        tab3 = QTextEdit()
        tab3.setStyleSheet("QTextEdit { margin: 5px; border: 1px solid lightgrey}")
        tab3.setFrameStyle(QFrame.NoFrame)
        tab3.setFont(font)

        # Add tabs
        tabs.addTab(tab1, "Source")
        tabs.addTab(tab2, "Tokens")
        tabs.addTab(tab3, "Export definition")

        rightsplitter.addWidget(tabs)

        self.sourceCode = tab1
        self.assemblyCode = tab2
        self.symbolDetails = self.createSymbolDetailsWidget(parent=rightsplitter)

        self.setWindowTitle('PyDecDat')
        self.statusBar()
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 900, 680)
        self.show()

    def search(self):
        search_text = self.searchInput.text()

        symbols = [symbol for symbol in self.dat.symbols if search_text in symbol.name]

        self.show_symbols(symbols)

        print(search_text)

    def createSymbolDetailsWidget(self, parent):
        symbolDetails = QTableWidget()
        symbolDetails.setEditTriggers(QAbstractItemView.NoEditTriggers)
        symbolDetails.setColumnCount(2)
        symbolDetails.setRowCount(len(ROWS))
        symbolDetails.horizontalHeader().hide()
        symbolDetails.verticalHeader().hide()
        symbolDetails.verticalHeader().setDefaultSectionSize(16)

        header = symbolDetails.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        for i, row in enumerate(ROWS):
            if isinstance(row, tuple):
                row = row[-1]
            symbolDetails.setItem(i, 0, QTableWidgetItem(row))

        parent.addWidget(symbolDetails)
        return symbolDetails

    def createSymbolsTableWidget(self, parent):
        symbolsTable = QTableWidget()
        symbolsTable.setSortingEnabled(True)
        symbolsTable.itemSelectionChanged.connect(self.onSelectSymbol)
        symbolsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        symbolsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        symbolsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        symbolsTable.setColumnCount(4)  # FIXME: 3

        font = QFont()
        font.setPointSize(10)
        font.setFamily("Courier New")
        symbolsTable.setFont(font)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setFamily(app.font().family())
        symbolsTable.horizontalHeader().setFont(font)
        symbolsTable.verticalHeader().setDefaultSectionSize(16)

        item_id = QTableWidgetItem('Id')
        item_id.setBackground(QColor(240, 240, 240))
        symbolsTable.setHorizontalHeaderItem(0, item_id)

        item_symbolname = QTableWidgetItem('Symbol name')
        item_symbolname.setBackground(QColor(240, 240, 240))
        symbolsTable.setHorizontalHeaderItem(1, item_symbolname)

        item_type = QTableWidgetItem('Type')
        item_type.setBackground(QColor(240, 240, 240))
        symbolsTable.setHorizontalHeaderItem(2, item_type)

        item_sort_id = QTableWidgetItem('Sort Id')
        item_sort_id.setBackground(QColor(240, 240, 240))
        symbolsTable.setHorizontalHeaderItem(3, item_sort_id)

        symbolsTable.verticalHeader().hide()
        header = symbolsTable.horizontalHeader()
        header.setStretchLastSection(True)

        parent.addWidget(symbolsTable)
        return symbolsTable

    def export_all(self):
        # symbol = self.dat.symbols[10229]
        # print(symbol.id)
        # print('TOKENS')
        # print(get_tokens(symbol))
        # print('CODE')
        # print(get_code(symbol))
        #
        # return
        with open('output.d', 'w') as file:

            for symbol in self.dat.symbols:
                print('symbol.id', symbol.id)
                code = get_code(symbol)
                if '.' in symbol.name:
                    _, right_size = symbol.name.split('.')
                    if not right_size.startswith('par'):
                        print("DAMM", symbol.id)
                        # exit()
                    continue

                file.write(code)
                file.write('\n')
                print(code)




    def about(self):
        QMessageBox.about(self, "Daedalus Decompiler", "Version 1.1, based of DecDat by Gottfried - 2012")

    def selectDat(self):
        options = QFileDialog.Options()
        fileDialog = QFileDialog()

        filePath, _ = fileDialog.getOpenFileName(
            caption='Open .dat file',
            filter='Compiled Daedalus Script (*.dat *.DAT);;All Files (*)',
            options=options,
        )

        if not filePath:
            return

        self.setCursor(Qt.WaitCursor)  # FIXME
        self.dat = Dat(filePath)
        Token.dat = self.dat
        self.show_symbols(self.dat.symbols)
        self.unsetCursor()  # FIXME
        # self.decompiler = Decompiler(dat=self.dat)

    def show_symbols(self, symbols):
        if not symbols:
            print('Empty symbols list.')  # ignore request.
            return

        self.symbolsTable.setRowCount(len(symbols))
        for i, symbol in enumerate(symbols):
            self.symbolsTable.setItem(i, 0, TableWidgetItemWithNumber(str(symbol.id)))
            self.symbolsTable.setItem(i, 1, QTableWidgetItem(symbol.name))
            self.symbolsTable.setItem(i, 2, QTableWidgetItem(symbol.type_as_str))
            self.symbolsTable.setItem(i, 3, TableWidgetItemWithNumber(str(symbol.sort_table_id)))

    def onSelectSymbol(self):
        item_id, item_symbolname, item_type, item_sort_id = self.symbolsTable.selectedItems()
        symbol_id = int(item_id.text())
        symbol = mainWindow.dat.symbols[symbol_id]

        print(symbol_id, item_symbolname.text(), item_type.text())
        # code = self.decompiler.get_code(symbol)
        code = get_code(symbol)
        self.sourceCode.setText(code)

        assembly = get_code(symbol, assembly=True)
        self.assemblyCode.setText(assembly)

        for i, row in enumerate(ROWS):
            display_data = ''
            if isinstance(row, tuple):
                display_row_name = row[-1]
                for row_name in row:
                    attr = getattr(symbol, row_name)
                    if attr is not None:
                        display_data = str(attr)
                        display_row_name = row_name
                        break
                self.symbolDetails.setItem(i, 0, QTableWidgetItem(display_row_name))
            else:
                attr = getattr(symbol, row)
                display_data = str(attr)

            self.symbolDetails.setItem(i, 1, QTableWidgetItem(display_data))



def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    app = QApplication(sys.argv)
    # QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    # QApplication.restoreOverrideCursor()
    # QApplication.overrideCursor()

    app.setStyle(QStyleFactory.create('GTK+'))  # GTK+/Windows/Fusion
    print(app.font().family(), app.font().defaultFamily())
    mainWindow = MainWindow()
    decompiler.mainWindow = mainWindow
    sys.exit(app.exec_())
