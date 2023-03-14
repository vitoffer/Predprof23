from PyQt5 import uic
from TableViewRace import *



class Race(QMainWindow):
    def __init__(self, race_id, parent):
        super(Race, self).__init__(parent)
        uic.loadUi('RaceView.ui', self)
        self.id = race_id
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        a = cur.execute(f'SELECT pilots_numbers FROM races WHERE race_id={self.id}').fetchone()[0].split(', ')
        self.pilot1_num = a[0]
        if len(a) == 1:
            self.num_pilots = 1
            self.pilot2Button.setEnabled(False)
        else:
            self.num_pilots = 2
            self.pilot2_num = a[1]
        self.pilot = 1

        #isFinished:
        if cur.execute(f'SELECT isFinished FROM races WHERE race_id={self.id}').fetchone()[0] == 'True':
            self.isFinished = True
        else:
            self.isFinished = False
        if self.isFinished:
            self.isStartedlabel.setText('Заезд завершён')
            self.startButton.setEnabled(False)
            self.tableViewButton.setEnabled(True)
            self.pilot2Button.setEnabled(False)
        else:
            self.startButton.setEnabled(True)
            self.tableViewButton.setEnabled(False)
            a = cur.execute(f'SELECT pilot1 FROM race_{self.id}').fetchone()
            b = cur.execute(f'SELECT pilot2 FROM race_{self.id}').fetchone()
            if a is None and b is None:
                self.isStartedlabel.setText('Заезд не начат')
                self.isFinished2 = False
                self.isFinished1 = False
            elif a[0] is None:
                self.isFinished1 = False
                self.isFinished2 = True
                self.isStartedlabel.setText(f'Заезд не начат для пилота {self.pilot1_num}')
            elif b[0] is None and self.num_pilots == 2:
                self.isFinished2 = False
                self.isFinished1 = True
                self.startButton.setEnabled(False)
                self.isStartedlabel.setText(f'Заезд не начат для пилота {self.pilot2_num}')
            else:
                self.isStartedlabel.setText('Заезд не начат')
                self.isFinished2 = False
                self.isFinished1 = False


        #buttons:
        self.pilot1Button.setEnabled(False)
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
        self.graphWidget.setYRange(-200, 200)
        self.graphWidget.setXRange(0, 30)
        self.pen1 = pg.mkPen(color=(255, 0, 0))
        self.pen2 = pg.mkPen(color=(0, 0, 255))



        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()

    def table_view(self):
        self.hide()
        self.table_v = TableView(self.id, self.num_pilots, self)
        self.table_v.show()
        self.table_v.load()

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def load(self):
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        if self.isFinished:
            self.x = list(float(_[0]) for _ in cur.execute(f'SELECT time FROM race_{str(self.id)}').fetchall())
            self.y1 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot1 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y1, "Pilot1", 'r')
            if self.num_pilots == 2:
                self.y2 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot2 FROM race_{str(self.id)}').fetchall())
                self.plot(self.x, self.y2, "Pilot2", 'b')
        elif self.isFinished1:
            self.x = list(float(_[0]) for _ in cur.execute(f'SELECT time FROM race_{str(self.id)}').fetchall())
            self.y1 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot1 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y1, "Pilot1", 'r')
        elif self.isFinished2:
            self.x = list(float(_[0]) for _ in cur.execute(f'SELECT time FROM race_{str(self.id)}').fetchall())
            self.y2 = list(float(_[0]) for _ in cur.execute(f'SELECT pilot2 FROM race_{str(self.id)}').fetchall())
            self.plot(self.x, self.y2, "Pilot2", 'b')
        cur.close()
        sqlite_connection.close()



    def save(self):
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        self.x = [round(i, 1) for i in np.arange(0, 30.1, 0.1)]
        finish1, finish2 = False, False
        if self.pilot == 1:
            if self.num_pilots == 2 and self.isFinished2:
                last_data2 = cur.execute(f'SELECT * FROM race_{self.id}').fetchall()
                finish2 = True
                last_time = [_[0] for _ in last_data2]
                last_pilot2 = [_[2] for _ in last_data2]
                cur.execute(f'DELETE FROM race_{self.id}')
                sqlite_connection.commit()
            self.y1 = self.y1[::2]
            a = float(self.y1[0])
            self.y1 = self.y1[1:]
            self.y1 = self.y1[:-1]
            self.y1 = [str((float(i) - a) - ((float(i) - a) % 5)) for i in self.y1]
            self.y1.insert(0, '0')
            ln = len(self.y1)
            y1_up = [self.y1[-1]] * (301 - ln)
            if ln < 301:
                self.y1.extend(y1_up)
            elif ln > 301:
                self.y1 = self.y1[:301]
            self.y1.append(self.y1[-1])

            cur.execute('UPDATE races SET end_time=? WHERE race_id=?', (str(datetime.datetime.now().isoformat(sep=' ')).split(' ')[1], self.id))
            sqlite_connection.commit()
        else:
            if self.num_pilots == 2 and self.isFinished1:
                last_data1 = cur.execute(f'SELECT * FROM race_{self.id}').fetchall()
                finish1 = True
                last_time = [_[0] for _ in last_data1]
                last_pilot1 = [_[1] for _ in last_data1]
                cur.execute(f'DELETE FROM race_{self.id}')
                sqlite_connection.commit()
            else:
                cur.execute('UPDATE races SET end_time=? WHERE race_id=?', (str(datetime.datetime.now().isoformat(sep=' ')).split(' ')[1], self.id))
                sqlite_connection.commit()
            self.y2 = self.y2[::2]
            a = float(self.y2[0])
            self.y2 = self.y2[1:]
            self.y2 = self.y2[:-1]
            self.y2 = [str((float(i) - a) - ((float(i) - a) % 5)) for i in self.y2]
            self.y2.insert(0, '0')
            ln = len(self.y2)
            y2_up = [self.y2[-1]] * (301 - ln)
            if ln < 301:
                self.y2.extend(y2_up)
            elif ln > 301:
                self.y2 = self.y2[:301]
            self.y2.append(self.y2[-1])



        for i in range(301):
            if self.pilot == 1:
                if finish2:
                    cur.execute(f'INSERT OR IGNORE INTO race_{self.id} (time, pilot1, pilot2) VALUES(?, ?, ?)',
                                (last_time[i], self.y1[i], last_pilot2[i]))
                else:
                    cur.execute(f'INSERT OR IGNORE INTO race_{self.id} (time, pilot1, pilot2) VALUES(?, ?, ?)', (self.x[i], self.y1[i], None))
            else:
                if finish1:
                    cur.execute(f'INSERT OR IGNORE INTO race_{self.id} (time, pilot1, pilot2) VALUES(?, ?, ?)',
                                (last_time[i], last_pilot1[i], self.y2[i]))
                else:
                    cur.execute(f'INSERT OR IGNORE INTO race_{self.id} (time, pilot1, pilot2) VALUES(?, ?, ?)', (self.x[i], None, self.y2[i]))
        if self.num_pilots == 1:
            self.isFinished = True
            cur.execute(f'UPDATE races SET isFinished="True" WHERE race_id ={self.id}')
        elif self.num_pilots == 2:
            if self.pilot == 1 and not self.isFinished2:
                self.isFinished1 = True
            elif self.pilot == 2 and not self.isFinished1:
                self.isFinished2 = True
            else:
                self.isFinished = True
                cur.execute(f'UPDATE races SET isFinished="True" WHERE race_id ={self.id}')

        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()
        self.tableViewButton.setEnabled(True)

    def back(self):
        self.close()
        self.parent().show()

    def change_to_pilot1(self):
        self.pilot1Button.setEnabled(False)
        self.pilot = 1
        if not self.isFinished1:
            self.startButton.setEnabled(True)
        if self.isFinished2:
            self.pilot2Button.setEnabled(False)
        else:
            self.pilot2Button.setEnabled(True)

    def change_to_pilot2(self):
        self.pilot2Button.setEnabled(False)
        self.pilot = 2
        if not self.isFinished2:
            self.startButton.setEnabled(True)
        if self.isFinished1:
            self.pilot1Button.setEnabled(False)
        else:
            self.pilot1Button.setEnabled(True)

    def start(self):
        # url = 'http://esp8266.local/start'
        # req = requests.get(url)
        self.sock.send('start'.encode('utf-8'))
        self.isStartedlabel.setText(f'Заезд начался...')
        self.pilot1Button.setEnabled(False)
        self.pilot2Button.setEnabled(False)
        self.startButton.setEnabled(False)
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.finish)
        self.timer.start(15000)
        sqlite_connection = sqlite3.connect('./data/data.db')
        cur = sqlite_connection.cursor()
        if not self.isFinished1 and not self.isFinished2:
            cur.execute('UPDATE races SET start_time=? WHERE race_id=?', (str(datetime.datetime.now().isoformat(sep=' ')).split(' ')[1], self.id))
        sqlite_connection.commit()
        cur.close()
        sqlite_connection.close()

    def finish(self):
        # url = 'http://esp8266.local/download'
        # req = requests.get(url)
        self.sock.send('finish'.encode('utf-8'))
        data = bytearray(self.sock.recv(4096))
        ans = str(data.decode('utf-8'))
        tst = ""
        while ("fn" not in ans):
            tst += ans
            data = bytearray(self.sock.recv(4096))
            ans = str(data.decode('utf-8'))
        print(tst)
        tst += ans

        if self.pilot == 2:
            self.y2 = tst.split(";\n")
            self.pilot1Button.setEnabled(True)
        if self.pilot == 1:
            self.y1 = tst.split(";\n")
            self.pilot2Button.setEnabled(True)
        self.isStartedlabel.setText('Заезд завершён')
        self.save()
        self.load()
        self.startButton.setEnabled(False)
