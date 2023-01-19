import sys

import sqlite3
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import time
matplotlib.use('Qt5Agg')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainWindow.ui', self)
        self.toTableButton.clicked.connect(self.to_table)
        self.exitButton.clicked.connect(self.exit)


    def to_table(self):
        self.t = TableWindow()
        self.t.show()
        self.hide()

    def exit(self):
        sys.exit()


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class TableWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(TableWindow, self).__init__(*args, **kwargs)
        uic.loadUi('table.ui', self)
        self.load()

        self.canvas = MplCanvas(self, width=4, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout.addWidget(self.canvas)
        self.verticalLayout.addWidget(toolbar)

        self.MenuButton.clicked.connect(self.to_main_menu)
        self.NewRaceButton.clicked.connect(self.create_new_race)
        self.StartButton.clicked.connect(self.start_race)

        self.tableWidget.cellClicked.connect(self.cell_was_clicked)

    def cell_was_clicked(self, row):
        self.canvas.axes.cla()
        self.canvas.axes.plot([-3, -2, -1, 0, 1, 2, 3], [9, 4, 1, 0, 1, 4, 9])
        self.canvas.draw()

    def to_main_menu(self):
        ex.show()
        self.hide()

    def create_new_race(self):
        id_race = QTableWidget.currentRow(self.tableWidget)
        print(id_race)
        new_race_data = NewRaceDialog()
        if new_race_data.exec():
            self.title = new_race_data.title_line.text()
            self.date = new_race_data.date_line.text()
            self.organizer = new_race_data.org_line.text()
            self.place = new_race_data.place_line.text()
            self.type = new_race_data.type_line.text()
            self.pilot1_num = new_race_data.pilot1_line.text()
            self.pilot2_num = new_race_data.pilot2_line.text()
            print(self.title, self.date, self.organizer, self.place, self.type)
            self.add_race_to_table()
            self.load()
        else:
            print(0)

    # def add_race_table(self):

    def add_race_to_table(self):
        try:
            sqlite_connection = sqlite3.connect('data.db')
            cursor = sqlite_connection.cursor()
            sqlite_create_table_query = f'''INSERT INTO main(race_id, title, date, organizer, place, race_type) VALUES(?, ?, ?, ?, ?, ?);'''
            dataCopy = cursor.execute("select count(*) from main")
            values = dataCopy.fetchone()
            cursor.execute(sqlite_create_table_query, (values[0], self.title, self.date,
                                                        self.organizer, self.place, self.type))
            sqlite_connection.commit()
            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def start_race(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.StartRace = Race()
            self.StartRace.show()
            self.hide()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()
        cur.execute("SELECT * FROM main")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            print(row[6])
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(row[1]))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(row[2]))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(row[3]))
            self.tableWidget.setItem(indx, 3, QTableWidgetItem(row[4]))
            self.tableWidget.setItem(indx, 4, QTableWidgetItem(row[5]))
            self.tableWidget.setItem(indx, 5, QTableWidgetItem(row[6]))
        cur.close()
        sqlite_connection.close()


class NewRaceDialog(QDialog):
    def __init__(self):
        super(NewRaceDialog, self).__init__()
        uic.loadUi('NewRace.ui', self)


class Race(QMainWindow):
    def __init__(self, parent=None):
        super(Race, self).__init__(parent)
        uic.loadUi('StartedRace.ui', self)
        self.progressBar.setValue(0)

        self.isStarted = False
        self.isFinished = False

        self.backButton.clicked.connect(self.back)
        self.startButton.clicked.connect(self.start)

        self.canvas = MplCanvas(self, width=4, height=4, dpi=100)
        self.canvas.axes.plot()
        toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(self.canvas)

    def back(self):
        ex.t.show()
        self.hide()

    def start(self):
        self.isStartedlabel.setText('Заезд начался')
        self.isStarted = True
        x = 0
        for i in range(5):
            x += 20
            self.progressBar.setValue(x)
            time.sleep(1)
        self.canvas.axes.plot([-3, -2, -1, 0, 1, 2, 3], [9, 4, 1, 0, 1, 4, 9])
        self.canvas.draw()
        self.finish()

    def finish(self):
        self.isFinished = True
        self.isStarted = False
        self.isStartedlabel.setText('Заезд завершён')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

