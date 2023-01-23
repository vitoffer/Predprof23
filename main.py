import sys

import sqlite3
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import numpy as np
import time
from random import randint


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


class TableWindow(QMainWindow):
    def __init__(self):
        super(TableWindow, self).__init__()
        uic.loadUi('table.ui', self)
        self.load()

        self.graphWidget = pg.PlotWidget()
        self.verticalLayout.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.graphWidget.setTitle("Угол", color="gray", size="15pt")
        styles = {'color': 'b', 'font-size': '10px'}
        self.graphWidget.setLabel('left', 'Угол (°)', **styles)
        self.graphWidget.setLabel('bottom', 'Время (с)', **styles)
        self.graphWidget.setYRange(-360, 360)
        self.graphWidget.setXRange(0, 60)

        self.MenuButton.clicked.connect(self.to_main_menu)
        self.NewRaceButton.clicked.connect(self.create_new_race)
        self.OpenDataButton.clicked.connect(self.view_race)
        self.DeleteButton.clicked.connect(self.delete)

        self.tableWidget.cellClicked.connect(self.cell_was_clicked)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def cell_was_clicked(self):
        self.graphWidget.clear()
        self.StartRace = Race(self.tableWidget.currentRow())
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()
        if f'race_{self.StartRace.id}' in [_[0] for _ in list(cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table"').fetchall())]:
            x = list(int(_[0]) for _ in cursor.execute(f'SELECT time FROM race_{self.StartRace.id}').fetchall())
            y1 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot1 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
            if self.StartRace.num_pilots == 2:
                y2 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot2 FROM race_{self.StartRace.id}').fetchall())
                self.plot(x, y2, "Pilot2", 'b')
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()

    def to_main_menu(self):
        ex.show()
        self.hide()

    def delete(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
            sqlite_connection = sqlite3.connect('data.db')
            cursor = sqlite_connection.cursor()
            cursor.execute(f'DELETE FROM main WHERE race_id="{self.StartRace.id}"')
            cursor.execute(f'DROP TABLE race_{self.StartRace.id}')
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            self.load()

    def create_new_race(self):
        new_race_data = NewRaceDialog()
        if new_race_data.exec():
            self.title = new_race_data.title_line.text()
            self.date = new_race_data.date_line.text()
            self.organizer = new_race_data.org_line.text()
            self.place = new_race_data.place_line.text()
            self.type = new_race_data.type_line.text()
            self.pilot1_num = new_race_data.pilot1_line.text()
            self.pilot2_num = new_race_data.pilot2_line.text()
            self.add_race_to_table()
            self.add_race_table()
            self.load()
        else:
            print(0)

    def add_race_table(self):
        sqlite_connection = sqlite3.connect('data.db')
        cursor = sqlite_connection.cursor()

        cursor.execute(f'''CREATE TABLE race_{self.tableWidget.rowCount()} (
                            time,
                            pilot1,
                            pilot2)''')
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()

    def add_race_to_table(self):
        try:
            sqlite_connection = sqlite3.connect('data.db')
            cursor = sqlite_connection.cursor()
            sqlite_create_table_query = f'''INSERT INTO main(race_id, title, date, organizer, place, race_type, pilots_numbers) VALUES(?, ?, ?, ?, ?, ?, ?);'''
            dataCopy = cursor.execute("select count(*) from main")
            values = dataCopy.fetchone()
            if self.pilot2_num != '':
                pilots = f'{self.pilot1_num}, {self.pilot2_num}'
            else:
                pilots = str(self.pilot1_num)
            cursor.execute(sqlite_create_table_query, (values[0], self.title, self.date,
                                                        self.organizer, self.place, self.type, pilots))
            sqlite_connection.commit()
            cursor.close()

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")

    def view_race(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
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
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(str(row[2])))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(str(row[3])))
            self.tableWidget.setItem(indx, 3, QTableWidgetItem(str(row[4])))
            self.tableWidget.setItem(indx, 4, QTableWidgetItem(str(row[5])))
            self.tableWidget.setItem(indx, 5, QTableWidgetItem(str(row[6])))
        cur.close()
        sqlite_connection.close()


class NewRaceDialog(QDialog):
    def __init__(self):
        super(NewRaceDialog, self).__init__()
        uic.loadUi('NewRace.ui', self)


class Race(QMainWindow):
    def __init__(self, race_id):
        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()

        super(Race, self).__init__()
        uic.loadUi('StartedRace.ui', self)
        self.id = race_id

        if cur.execute(f'SELECT isFinished FROM main WHERE race_id={self.id}').fetchone()[0] == 'True':
            self.isFinished = True
            self.isStartedlabel.setText('Заезд завершён')
        else:
            self.isFinished = False
            self.isStartedlabel.setText('Заезд не начат')
        if self.isFinished:
            self.isStarted = True
        else:
            self.isStarted = False

        self.saveDataButton.setEnabled(False)
        self.backButton.clicked.connect(self.back)
        self.startButton.clicked.connect(self.start)
        self.saveDataButton.clicked.connect(self.save)
        self.tableViewButton.clicked.connect(self.table_view)
        if self.isFinished:
            self.startButton.setEnabled(False)
            self.tableViewButton.setEnabled(True)
        else:
            self.startButton.setEnabled(True)
            self.tableViewButton.setEnabled(False)

        self.graphWidget = pg.PlotWidget()
        self.layout.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Угол", color="gray", size="15pt")
        styles = {'color': 'b', 'font-size': '10px'}
        self.graphWidget.setLabel('left', 'Угол (°)', **styles)
        self.graphWidget.setLabel('bottom', 'Время (с)', **styles)
        self.graphWidget.setYRange(-360, 360)
        self.graphWidget.setXRange(0, 60)
        self.pen1 = pg.mkPen(color=(255, 0, 0))
        self.pen2 = pg.mkPen(color=(0, 0, 255))

        if cur.execute(f'SELECT race_type FROM main WHERE race_id={self.id}').fetchone()[0] == 'qualifying':
            self.num_pilots = 1
        else:
            self.num_pilots = 2

        if self.isFinished:
            x = list(int(_[0]) for _ in cur.execute(f'SELECT time FROM race_{self.id}').fetchall())
            y1 = list(int(_[0]) for _ in cur.execute(f'SELECT pilot1 FROM race_{self.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
            if self.num_pilots == 2:
                y2 = list(int(_[0]) for _ in cur.execute(f'SELECT pilot2 FROM race_{self.id}').fetchall())
                self.plot(x, y2, "Pilot2", 'b')
        else:
            self.x = list(range(10))
            self.y1 = [randint(-300, 300) for _ in range(10)]
            self.data_line1 = self.graphWidget.plot(self.x, self.y1, pen=self.pen1)
            if self.num_pilots == 2:
                self.y2 = [randint(-300, 300) for _ in range(10)]
                self.data_line2 = self.graphWidget.plot(self.x, self.y2, pen=self.pen2)

        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()

    def table_view(self):
        self.hide()
        self.table_v = TableViewRace()
        self.table_v.show()
        self.table_v.load()

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def save(self):
        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()
        cur.execute(f'UPDATE main SET isFinished="True" WHERE race_id = "{self.id}"')
        if self.num_pilots == 2:
            for i in range(len(self.y1)):
                cur.execute(f'''INSERT INTO race_{self.id} VALUES (?, ?, ?)''', (str(self.x[i]), str(self.y1[i]), str(self.y2[i])))
        else:
            for i in range(len(self.y1)):
                cur.execute(f'''INSERT INTO race_{self.id} VALUES (?, ?, ?)''', (str(self.x[i]), str(self.y1[i]), ''))
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
        self.saveDataButton.setEnabled(False)
        self.tableViewButton.setEnabled(True)

    def back(self):
        self.close()
        ex.t.show()

    def start(self):
        self.isStartedlabel.setText('Заезд начался')
        self.isStarted = True
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.x.append(self.x[-1] + 1)
        if self.x[-1] > 50:
            self.finish()
            return

        self.y1.append(randint(-360, 360))
        self.data_line1.setData(self.x, self.y1)
        if self.num_pilots == 2:
            self.y2.append(randint(-360, 360))
            self.data_line2.setData(self.x, self.y2)

    def finish(self):
        self.timer.stop()
        self.isFinished = True
        self.isStartedlabel.setText('Заезд завершён')
        self.saveDataButton.setEnabled(True)
        self.startButton.setEnabled(False)


class TableViewRace(QMainWindow):
    def __init__(self):
        super(TableViewRace, self).__init__()
        uic.loadUi('Race.ui', self)
        self.MenuButton.clicked.connect(self.menu)
        self.toGraphButton.clicked.connect(self.graph_view)
        self.toTableButton.clicked.connect(self.to_table)

        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()
        r_type = cur.execute(f"SELECT race_type FROM main WHERE race_id={ex.t.StartRace.id}").fetchone()[0]
        self.type_label.setText(f'Тип заезда: {r_type}')
        pilot1 = cur.execute(f"SELECT pilots_numbers FROM main WHERE race_id={ex.t.StartRace.id}").fetchone()[0].split(', ')[0]
        self.tableWidget.horizontalHeaderItem(1).setText(f'Пилот {pilot1}')
        if ex.t.StartRace.num_pilots == 2:
            pilot2 = cur.execute(f"SELECT pilots_numbers FROM main WHERE race_id={ex.t.StartRace.id}").fetchone()[0].split(', ')[1]
            self.tableWidget.horizontalHeaderItem(2).setText(f'Пилот {pilot2}')
        else:
            self.tableWidget.horizontalHeaderItem(2).setText('Нет')
        cur.close()
        sqlite_connection.close()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()
        cur.execute(f"SELECT * FROM race_{ex.t.StartRace.id}")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(str(row[2])))
        cur.close()
        sqlite_connection.close()

    def menu(self):
        self.close()
        ex.show()

    def graph_view(self):
        self.close()
        ex.t.StartRace.show()

    def to_table(self):
        self.close()
        ex.t.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
