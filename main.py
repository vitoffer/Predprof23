import sys

import sqlite3
from PyQt5 import uic
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainWindow.ui', self)
        self.pushButton.clicked.connect(self.to_table)

    def to_table(self):
        self.t = TableWindow()
        self.t.show()
        self.hide()


class TableWindow(MainWindow):
    def __init__(self):
        super(TableWindow, self).__init__()
        uic.loadUi('table.ui', self)
        self.load()
        self.MenuButton.clicked.connect(self.to_main_menu)
        self.NewRaceButton.clicked.connect(self.create_new_race)
        self.OpenDataButton.clicked.connect(self.start_race)


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
        #arduino
        pass

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('data.db')
        cur = sqlite_connection.cursor()
        cur.execute("SELECT * FROM main")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(row[1]))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(row[2]))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(row[3]))
            self.tableWidget.setItem(indx, 3, QTableWidgetItem(row[4]))
            self.tableWidget.setItem(indx, 4, QTableWidgetItem(row[5]))
        cur.close()
        sqlite_connection.close()


class NewRaceDialog(QDialog):
    def __init__(self):
        super(NewRaceDialog, self).__init__()
        uic.loadUi('NewRace.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

