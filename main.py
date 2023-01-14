import csv
import sys

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
        self.tableWidget.insertRow(0)
        self.tableWidget.insertRow(0)
        self.MenuButton.clicked.connect(self.to_main_menu)
        self.NewRaceButton.clicked.connect(self.create_new_race)

    def to_main_menu(self):
        ex.show()
        self.hide()

    def create_new_race(self):
        id_race = QTableWidget.currentRow(self.tableWidget)
        print(id_race)
        new_race_data = NewRaceDialog()
        if new_race_data.exec():
            title = new_race_data.title_line.text()
            date = new_race_data.date_line.text()
            organizer = new_race_data.org_line.text()
            place = new_race_data.place_line.text()
            type = new_race_data.type_line.text()
            print(title, date, organizer, place, type)
        else:
            print(0)


class NewRaceDialog(QDialog):
    def __init__(self):
        super(NewRaceDialog, self).__init__()
        uic.loadUi('NewRace.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
