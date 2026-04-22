import sys

from PyQt5 import QtWidgets
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QMessageBox

import pyodbc

import test

class Data_Base:
    def __init__(self):
        self.server = 'localhost\\SQLEXPRESS'
        self.database = 'data_world_4'
        self.username = 'root'
        self.password = ''
        self.driver = 'ODBC Driver 17 for SQL Server'
        self.connection = None

    def connect(self):
        try:
            self.connection = pyodbc.connect(
                f'DRIVER={{{self.driver}}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
            )
            return True
        except pyodbc.Error as e:
            print(e)
            return False

    def Set_Data(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('select * from Лаборанты')
            rows = cursor.fetchall()
            for row in rows:
                print(row)

            return rows
        except pyodbc.Error as e:
            print(e)
            return False


class TestWindow(QtWidgets.QMainWindow, test.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Test")

        self.Done_Button.clicked.connect(self.switch_window)

        self.db = Data_Base()
        self.db.connect()

        self.tableWidget.setRowCount(len(self.db.Set_Data()))
        self.tableWidget.setColumnCount(len(self.db.Set_Data()[0]))

        # headers = [
        #     'Код_лаборанта',
        #     'Код_лаборанта_системный',
        #     'Код_роли_системный',
        #     'Логин_пользователя',
        #     'Пароль_пользователя',
        #     'Фамилия_пользователя',
        #     'Имя_пользователя',
        #     'Отчество_пользователя',
        #     'Последняя_дата_входа',
        #     'Последнее_время_входа'
        # ]

        for i, row in enumerate(self.db.Set_Data()):
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))


    def switch_window(self, window = None):
        self.hide()
        if window is not None:
            self._window = TestWindow()
            QMessageBox.information(self,"Сохранено!","Успешное выполнение!")
            self._window.show()
        else:
            QMessageBox.warning(self,"Ошибка!", "Ошибка сохранения!")

class TestWindow2(QtWidgets.QMainWindow, test.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Test2")

        self.Done_Button.clicked.connect(self.switch_window)

    def switch_window(self, window = None):
        self.hide()
        if window is not None:
            self._window = TestWindow()
            QMessageBox.information(self,"Сохранено!","Успешное выполнение!")
            self._window.show()
        else:
            QMessageBox.warning(self,"Ошибка!", "Ошибка сохранения!")



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
