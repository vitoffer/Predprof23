import sqlite3
import sys
import datetime

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import requests
import numpy as np
import os
from RaceView import *


class RacesTableWindow(QMainWindow):
    def __init__(self, comp_id, parent):
        super(RacesTableWindow, self).__init__(parent)
        uic.loadUi('RacesTable.ui', self)
        self.id = comp_id
        self.load()
        self.StartRace = None
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #graphWidget:
        self.graphWidget = pg.PlotWidget()
        self.verticalLayout.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Угол", color="gray", size="15pt")
        styles = {'color': 'b', 'font-size': '10px'}
        self.graphWidget.setLabel('left', 'Угол (°)', **styles)
        self.graphWidget.setLabel('bottom', 'Время (с)', **styles)
        self.graphWidget.setYRange(-200, 200)
        self.graphWidget.setXRange(0, 30)

        #button clicks:
        self.MenuButton.clicked.connect(self.to_competitions)
        self.NewRaceButton.clicked.connect(self.create_new_race)
        self.OpenDataButton.clicked.connect(self.view_race)
        self.DeleteButton.clicked.connect(self.delete)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def cell_was_clicked(self):
        self.graphWidget.clear()
        self.StartRace = Race(int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text()), self)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cursor = sqlite_connection.cursor()
        x = list(float(_[0]) for _ in cursor.execute(f'SELECT time FROM race_{self.StartRace.id}').fetchall())
        if self.StartRace.isFinished:
            y1 = list(float(_[0]) for _ in cursor.execute(f'SELECT pilot1 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
            if self.StartRace.num_pilots == 2:
                y2 = list(float(_[0]) for _ in cursor.execute(f'SELECT pilot2 FROM race_{self.StartRace.id}').fetchall())
                self.plot(x, y2, "Pilot2", 'b')
        elif self.StartRace.isFinished1:
            y1 = list(float(_[0]) for _ in cursor.execute(f'SELECT pilot1 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
        elif self.StartRace.isFinished2:
            y2 = list(float(_[0]) for _ in cursor.execute(f'SELECT pilot2 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y2, "Pilot2", 'b')

        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()

    def to_competitions(self):
        self.close()
        self.parent().show()

    def delete(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            cursor.execute(f'DELETE FROM races WHERE race_id={self.StartRace.id} AND comp_id={self.id}')
            cursor.execute(f'DROP TABLE race_{self.StartRace.id}')
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            self.load()

    def create_new_race(self):
        new_race_data = NewRaceDialog(self)
        if new_race_data.exec():
            type = new_race_data.type_line.text()
            pilot1_num = new_race_data.pilot1_line.text()
            pilot2_num = new_race_data.pilot2_line.text()
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert = 'INSERT INTO races(race_id, comp_id, type, pilots_numbers, isFinished, start_time, end_time) VALUES(?, ?, ?, ?, ?, ?, ?)'
            dataCopy = cursor.execute("select * from races").fetchall()
            if len(dataCopy) == 0:
                last_id = 1
            else:
                last_id = int(dataCopy[-1][0]) + 1
            if pilot2_num == '':
                cursor.execute(sqlite_insert, (last_id, self.id, type, pilot1_num, "False", None, None))
            else:
                cursor.execute(sqlite_insert, (last_id, self.id, type, ', '.join([pilot1_num, pilot2_num]), "False", None, None))
            cursor.execute(f'CREATE TABLE race_{last_id}(time REAL, pilot1, pilot2)')
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            new_race_data.close()
            self.load()
        else:
            pass

    def view_race(self):
        if not (self.tableWidget.currentRow() + 1) or self.StartRace is None:
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
            self.StartRace.bd_addr = "00:18:E4:34:E4:B8"
            self.StartRace.port = 1
            self.StartRace.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.StartRace.sock.connect((self.StartRace.bd_addr, self.StartRace.port))
            self.hide()
            self.StartRace.show()
            self.StartRace.load()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute(f"SELECT * FROM races WHERE comp_id={self.id}")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(str(row[2])))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(str(row[3])))
        cur.close()
        sqlite_connection.close()


class NewRaceDialog(QDialog):
    def __init__(self, parent=None):
        super(NewRaceDialog, self).__init__(parent)
        uic.loadUi('NewRace.ui', self)
        self._want_to_close = False

    def closeEvent(self, evnt):
        if self._want_to_close:
            super(NewRaceDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
