import sqlite3

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class TableView(QMainWindow):
    def __init__(self, id, num_pilots, parent):
        super(TableView, self).__init__(parent)
        uic.loadUi('TableViewRace.ui', self)
        self.toGraphButton.clicked.connect(self.graph_view)
        self.id = id
        self.num_pilots = num_pilots
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        r_type = cur.execute(f"SELECT type FROM races WHERE race_id={self.id}").fetchone()[0]
        self.type_label.setText(f'Тип заезда: {r_type}')
        pilot1 = cur.execute(f"SELECT pilots_numbers FROM races WHERE race_id={self.id}").fetchone()[0].split(', ')[0]
        self.tableWidget.horizontalHeaderItem(1).setText(f'Пилот {pilot1}')
        if self.num_pilots == 2:
            pilot2 = cur.execute(f"SELECT pilots_numbers FROM races WHERE race_id={self.id}").fetchone()[0].split(', ')[1]
            self.tableWidget.horizontalHeaderItem(2).setText(f'Пилот {pilot2}')
        else:
            self.tableWidget.horizontalHeaderItem(2).setText('Нет')
        sql_sel_start = cur.execute(f'SELECT start_time FROM races WHERE race_id={self.id}').fetchone()[0]
        sql_sel_end = cur.execute(f'SELECT end_time FROM races WHERE race_id={self.id}').fetchone()[0]

        self.start_time_label.setText(f'''Время начала заезда:
{sql_sel_start}''')
        self.end_time_label.setText(f'''Время окончания заезда:
{sql_sel_end}''')
        cur.close()
        sqlite_connection.close()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute(f"SELECT * FROM race_{self.id}")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(str(row[2])))
        cur.close()
        sqlite_connection.close()

    def graph_view(self):
        self.close()
        self.parent().show()