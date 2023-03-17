from PyQt5 import uic
from RacesTable import *


class CompsTableWindow(QMainWindow):
    def __init__(self, parent):
        super(CompsTableWindow, self).__init__(parent)
        uic.loadUi('CompetitionsTable.ui', self)
        self.addButton.clicked.connect(self.add_competition)
        self.deleteButton.clicked.connect(self.delete_competition)
        self.menuButton.clicked.connect(self.to_main_menu)
        self.toRacesButton.clicked.connect(self.view_competition)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.load()
        self.Competition = None
        self.setWindowIcon(QtGui.QIcon('icon.png'))

    def add_competition(self):
        new_comp_data = NewCompetitionDialog(self)
        if new_comp_data.exec():
            title = new_comp_data.title_line.text()
            date = new_comp_data.calendarWidget.selectedDate().toString('dd-MM-yyyy')
            organizer = new_comp_data.organizer_line.text()
            place = new_comp_data.place_line.text()
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert = f'INSERT INTO competitions(comp_id, title, date, organizer, place) VALUES(?, ?, ?, ?, ?)'
            dataCopy = cursor.execute("select * from competitions").fetchall()
            if len(dataCopy) == 0:
                last_id = 1
            else:
                last_id = int(dataCopy[-1][0]) + 1
            cursor.execute(sqlite_insert, (last_id, title, date, organizer, place))
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            new_comp_data.close()
            self.load()
        else:
            pass

    def delete_competition(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            cursor.execute(f'DELETE FROM competitions WHERE comp_id="{self.Competition.id}"')
            for i in cursor.execute(f'SELECT race_id from races WHERE comp_id={self.Competition.id}').fetchall():
                cursor.execute(f'DROP table race_{i[0]}')
            cursor.execute(f'DELETE FROM races WHERE comp_id="{self.Competition.id}"')

            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            self.load()

    def cell_was_clicked(self):
        a = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        self.Competition = RacesTableWindow(int(a.text()), self)

    def view_competition(self):
        if not (self.tableWidget.currentRow() + 1) or self.Competition is None:
            self.label_selectRow.setText('Сначала выберите соревнование!')
        else:
            self.label_selectRow.setText('')
            self.Competition.show()
            self.hide()

    def to_main_menu(self):
        self.close()
        self.parent().show()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute("SELECT * FROM competitions")
        rows = cur.fetchall()
        for row in rows:
            indx = rows.index(row)
            self.tableWidget.insertRow(indx)
            self.tableWidget.setItem(indx, 0, QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(indx, 1, QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(indx, 2, QTableWidgetItem(str(row[2])))
            self.tableWidget.setItem(indx, 3, QTableWidgetItem(str(row[3])))
            self.tableWidget.setItem(indx, 4, QTableWidgetItem(str(row[4])))
        cur.close()
        sqlite_connection.close()


class NewCompetitionDialog(QDialog):
    def __init__(self, parent=None):
        super(NewCompetitionDialog, self).__init__(parent)
        uic.loadUi('NewCompetition.ui', self)
        self._want_to_close = False

    def closeEvent(self, evnt):
        if self._want_to_close:
            super(NewCompetitionDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
