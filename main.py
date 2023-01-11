import csv
import sys

from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('MainWindow.ui', self)
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setColumnWidth(1, 300)
        self.tableWidget.setColumnWidth(2, 300)
        self.tableWidget.setColumnWidth(3, 300)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())