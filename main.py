import sqlite3
import sys
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from CompetitionsTable import *
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('MainWindow.ui', self)
        self.toTableButton.clicked.connect(self.to_table)
        self.exitButton.clicked.connect(self.exit)

    def to_table(self):
        self.hide()
        self.table = CompsTableWindow()
        self.table.show()

    def exit(self):
        sys.exit()


class CompsTableWindow(QMainWindow):
    def __init__(self):
        super(CompsTableWindow, self).__init__()
        uic.loadUi('CompetitionsTable.ui', self)
        self.addButton.clicked.connect(self.add_competition)
        self.deleteButton.clicked.connect(self.delete_competition)
        self.menuButton.clicked.connect(self.to_main_menu)
        self.toRacesButton.clicked.connect(self.view_competition)
        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.load()

    def add_competition(self):
        new_comp_data = NewCompetitionDialog()
        if new_comp_data.exec():
            title = new_comp_data.title_line.text()
            date = new_comp_data.date_line.text()
            organizer = new_comp_data.organizer_line.text()
            place = new_comp_data.place_line.text()
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert = f'INSERT INTO competitions(comp_id, title, date, organizer, place) VALUES(?, ?, ?, ?, ?)'
            dataCopy = cursor.execute("select * from competitions")
            last_id = int(dataCopy.fetchall()[-1][0]) + 1
            cursor.execute(sqlite_insert, (last_id, title, date, organizer, place))
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
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
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            self.load()

    def cell_was_clicked(self):
        a = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        self.Competition = RacesTableWindow(int(a.text()))

    def view_competition(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите соревнование!')
        else:
            self.label_selectRow.setText('')
            self.Competition.show()
            self.hide()

    def to_main_menu(self):
        self.close()
        ex.show()

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
    def __init__(self):
        super(NewCompetitionDialog, self).__init__()
        uic.loadUi('NewCompetition.ui', self)


class RacesTableWindow(QMainWindow):
    def __init__(self, comp_id):
        super(RacesTableWindow, self).__init__()
        uic.loadUi('RacesTable.ui', self)
        self.id = comp_id
        self.load()

        #graphWidget:
        self.graphWidget = pg.PlotWidget()
        self.verticalLayout.addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Угол", color="gray", size="15pt")
        styles = {'color': 'b', 'font-size': '10px'}
        self.graphWidget.setLabel('left', 'Угол (°)', **styles)
        self.graphWidget.setLabel('bottom', 'Время (с)', **styles)
        self.graphWidget.setYRange(-360, 360)
        self.graphWidget.setXRange(0, 60)

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
        self.StartRace = Race(int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text()))
        sqlite_connection = sqlite3.connect('./data/data.db')
        cursor = sqlite_connection.cursor()
        x = list(int(_[0]) for _ in cursor.execute(f'SELECT time FROM race_{self.StartRace.id}').fetchall())
        if self.StartRace.isFinished:
            y1 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot1 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
            if self.StartRace.num_pilots == 2:
                y2 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot2 FROM race_{self.StartRace.id}').fetchall())
                self.plot(x, y2, "Pilot2", 'b')
        elif self.StartRace.isFinished1:
            y1 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot1 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y1, "Pilot1", 'r')
        elif self.StartRace.isFinished2:
            y2 = list(int(_[0]) for _ in cursor.execute(f'SELECT pilot2 FROM race_{self.StartRace.id}').fetchall())
            self.plot(x, y2, "Pilot2", 'b')

        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()

    def to_competitions(self):
        self.close()
        ex.table.show()

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
        new_race_data = NewRaceDialog()
        if new_race_data.exec():
            type = new_race_data.type_line.text()
            pilot1_num = new_race_data.pilot1_line.text()
            pilot2_num = new_race_data.pilot2_line.text()
            sqlite_connection = sqlite3.connect('./data/data.db')
            cursor = sqlite_connection.cursor()
            sqlite_insert = 'INSERT INTO races(race_id, comp_id, type, pilots_numbers, isFinished) VALUES(?, ?, ?, ?, False)'
            dataCopy = cursor.execute("select * from races")
            last_id = int(dataCopy.fetchall()[-1][0]) + 1
            cursor.execute(sqlite_insert, (last_id, self.id, type, ', '.join([pilot1_num, pilot2_num])))
            print(last_id)
            cursor.execute(f'CREATE TABLE race_{last_id}(time REAL, pilot1, pilot2)')
            sqlite_connection.commit()
            cursor.close()
            sqlite_connection.close()
            self.load()
        else:
            pass

    def view_race(self):
        if not (self.tableWidget.currentRow() + 1):
            self.label_selectRow.setText('Сначала выберите заезд!')
        else:
            self.label_selectRow.setText('')
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
    def __init__(self):
        super(NewRaceDialog, self).__init__()
        uic.loadUi('NewRace.ui', self)


class Race(QMainWindow):
    def __init__(self, race_id):
        super(Race, self).__init__()
        uic.loadUi('RaceView.ui', self)
        self.id = race_id
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()

        a = cur.execute(f'SELECT pilots_numbers FROM races WHERE race_id={self.id}').fetchone()[0].split(', ')
        self.pilot1_num = a[0]
        if len(a) == 1:
            self.num_pilots = 1
        else:
            self.num_pilots = 2
            self.pilot2_num = a[1]
        self.pilot = 1

        #isFinished:
        if cur.execute(f'SELECT isFinished FROM races WHERE race_id={self.id} AND comp_id={ex.table.Competition.id}').fetchone()[0] == 'True':
            self.isFinished = True
        else:
            self.isFinished = False
        if self.isFinished:
            self.isStartedlabel.setText('Заезд завершён')
            self.startButton.setEnabled(False)
            self.tableViewButton.setEnabled(True)
        else:
            self.startButton.setEnabled(True)
            self.tableViewButton.setEnabled(False)
            if cur.execute(f'SELECT pilot1 FROM race_{self.id}').fetchone() is None and cur.execute(f'SELECT pilot2 FROM race_{self.id}').fetchone() is not None:
                self.isFinished1 = False
                self.isFinished2 = True
                self.isStartedlabel.setText(f'Заезд не начат для пилота {self.pilot1_num}')
            elif cur.execute(f'SELECT pilot2 FROM race_{self.id}').fetchone() is None and cur.execute(f'SELECT pilot1 FROM race_{self.id}').fetchone() is not None and self.num_pilots == 2:
                self.isFinished2 = False
                self.isFinished1 = True
                self.isStartedlabel.setText(f'Заезд не начат для пилота {self.pilot2_num}')
            else:
                self.isStartedlabel.setText('Заезд не начат')
                self.isFinished2 = False
                self.isFinished1 = False


        #buttons:
        self.pilot1Button.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.finish)
        self.backButton.clicked.connect(self.back)
        self.startButton.clicked.connect(self.start)
        self.tableViewButton.clicked.connect(self.table_view)
        self.pilot1Button.clicked.connect(self.change_to_pilot1)
        self.pilot2Button.clicked.connect(self.change_to_pilot2)

        #graphWidget:
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

        if cur.execute(f'SELECT time from race_{self.id}').fetchone() is None:
            self.x = [round(i, 1) for i in np.arange(0, 60.1, 0.1)]
            for i in self.x:
                cur.execute(f'INSERT INTO race_{self.id} (time) VALUES({i})')
        else:
            self.x = [i[0] for i in cur.execute(f'SELECT time FROM race_{self.id}').fetchall()]

        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()

    def table_view(self):
        self.hide()
        self.table_v = TableView()
        self.table_v.show()
        self.table_v.load()

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def load(self):
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        if self.isFinished:
            self.y1 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot1 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y1, "Pilot1", 'r')
            if self.num_pilots == 2:
                self.y2 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot2 FROM race_{str(self.id)}').fetchall())
                self.plot(self.x, self.y2, "Pilot2", 'b')
        elif self.isFinished1:
            self.y1 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot1 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y1, "Pilot1", 'r')
        elif self.isFinished2:
            self.y2 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot2 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y2, "Pilot2", 'b')
        cur.close()
        sqlite_connection.close()

    # def save(self):
    #     url = 'http://esp8266.local/download'
    #     req = requests.get(url).text.split(';\n')
    #     sqlite_connection = sqlite3.connection('./data/data.db')
    #     cur = sqlite_connection.cursor
    #     for i in range(len(req)):
    #         if not self.isFinished:
    #             cur.execute(f'INSERT INTO race_{self.race_id} (time) VALUES({str(self.x[i])})')
    #         if self.pilot1:
    #             cur.execute(f'INSERT INTO race_{self.race_id} (pilot1) VALUES({float(req[i])})')
    #         else:
    #             cur.execute(f'INSERT INTO race_{self.race_id} (pilot2) VALUES({float(req[i])})')
    #     cur.execute(f'UPDATE main SET isFinished="True" WHERE race_id = "{self.id}"')
    #     sqlite_connection.commit()
    #     cur.close()
    #     sqlite_connection.close()
    #     self.tableViewButton.setEnabled(True)

    def save(self):
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        print(self.y1)
        print(len(self.y1))
        for i in range(len(self.y1)):
            if self.pilot == 1:
                print(self.x[i])
                cur.execute(f'UPDATE race_{self.id} SET pilot1 = {self.y1[i]} WHERE time = {str(self.x[i])}')
            else:
                print(self.x[i])
                cur.execute(f'UPDATE race_{self.id} SET pilot2 = {self.y1[i]} WHERE time={str(self.x[i])}')
            cur.execute(f'UPDATE races SET isFinished="True" WHERE race_id = "{self.id}"')
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
        self.tableViewButton.setEnabled(True)

    def back(self):
        self.close()
        ex.table.Competition.show()

    def change_to_pilot1(self):
        self.pilot1Button.setEnabled(False)
        self.pilot2Button.setEnabled(True)
        self.pilot = 1

    def change_to_pilot2(self):
        self.pilot1Button.setEnabled(True)
        self.pilot2Button.setEnabled(False)
        self.pilot = 2

    def start(self):
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
        url = 'http://esp8266.local/start'
        req = requests.get(url)
        if req:
            self.isStartedlabel.setText(f'Заезд начался...')
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finish)
        self.timer.start(10000)

    def finish(self):
        url = 'http://esp8266.local/download'
        req = requests.get(url)
        if req:
            self.y1 = req.text.split(';\n')
        self.isStartedlabel.setText('Заезд завершён')
        self.save()
        self.load()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)


class TableView(QMainWindow):
    def __init__(self):
        super(TableView, self).__init__()
        uic.loadUi('TableViewRace.ui', self)
        self.MenuButton.clicked.connect(self.menu)
        self.toGraphButton.clicked.connect(self.graph_view)
        self.toTableButton.clicked.connect(self.to_table)

        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        r_type = cur.execute(f"SELECT race_type FROM main WHERE race_id={ex.table.Competition.StartRace.id}").fetchone()[0]
        self.type_label.setText(f'Тип заезда: {r_type}')
        pilot1 = cur.execute(f"SELECT pilots_numbers FROM main WHERE race_id={ex.table.Competition.StartRace.id}").fetchone()[0].split(', ')[0]
        self.tableWidget.horizontalHeaderItem(1).setText(f'Пилот {pilot1}')
        if ex.table.Competition.StartRace.num_pilots == 2:
            pilot2 = cur.execute(f"SELECT pilots_numbers FROM main WHERE race_id={ex.table.Competition.StartRace.id}").fetchone()[0].split(', ')[1]
            self.tableWidget.horizontalHeaderItem(2).setText(f'Пилот {pilot2}')
        else:
            self.tableWidget.horizontalHeaderItem(2).setText('Нет')
        cur.close()
        sqlite_connection.close()

    def load(self):
        self.tableWidget.setRowCount(0)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute(f"SELECT * FROM race_{ex.table.Competition.StartRace.id}")
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
        ex.table.Competition.StartRace.show()

    def to_table(self):
        self.close()
        ex.table.Competition.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not os.path.isfile('./data/data.db'):
        os.mkdir('./data')
        os.path.join('./data', 'data.db')
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        cur.execute('CREATE TABLE main (race_id INTEGER, race_type TEXT, title TEXT, date, organizer TEXT, place TEXT, pilots_numbers TEXT, isFinished TEXT)')
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())