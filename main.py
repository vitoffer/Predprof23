import sqlite3
import sys
import datetime

from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import requests
import numpy as np
import os
from CompetitionsTable import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainWindow.ui', self)
        self.toTableButton.clicked.connect(self.to_table)
        self.exitButton.clicked.connect(self.exit)
        self.setWindowIcon(QtGui.QIcon('icon.png'))

    def to_table(self):
        self.hide()
        self.table = CompsTableWindow(self)
        self.table.show()

    def exit(self):
        sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not os.path.isfile('./data/data.db'):
        os.mkdir('./data')
        os.path.join('./data', 'data.db')
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute('''CREATE TABLE competitions (
    comp_id   INTEGER,
    title     TEXT,
    date      TEXT,
    organizer TEXT,
    place     TEXT
)''')
        cur.execute('''CREATE TABLE races (
    race_id        INTEGER,
    comp_id        INTEGER,
    type           TEXT,
    pilots_numbers TEXT,
    isFinished     TEXT,
    start_time     TEXT,
    end_time       TEXT
)''')
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
