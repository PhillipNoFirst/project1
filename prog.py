import sys 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

import autorization_design
import workspace 
import analizes

import pyodbc

class DataBase():
    def __init__(self):
        self.server = 'localhost\\SQLEXPRESS'
        self.database = 'data_world_4'
        self.connection = None
    
    def connect(self, username, password):
        try:
            self.connection = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
                f'UID={username};'
                f'PWD={password};'
            )
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def checkUser(self, login, password):

        # chacking0 4tzqHdkqzo4

        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM Лаборанты WHERE Логин_пользователя = ? AND Пароль_пользователя = ?"
            cursor.execute(query, (login, password))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    def getName(self, login, password):
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT Имя_пользователя FROM Лаборанты WHERE Логин_пользователя = ? AND Пароль_пользователя = ?"
            cursor.execute(query, (login, password))
            result = cursor.fetchone()
            return result[0]
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
            

class Autorization(QtWidgets.QMainWindow, autorization_design.Ui_MainWindow):
    def __init__(self, window2 = None):
        super().__init__()
        self.setupUi(self)

        # подключение
        self.db = DataBase()
        self.db.connect()

        # ожидает нажатия, а после запускает смену окна
        self.EnterButton.clicked.connect(self.switchWindow)
        self._window2 = window2

        # маска для пароля
        self.plainPassword.setEchoMode(QtWidgets.QLineEdit.Password)

        # чекбокс чтобы показать пароль
        self.ShowPasswordCheckBox.stateChanged.connect(self.showPassword)

    def showPassword(self):
        if self.ShowPasswordCheckBox.isChecked():
            # показываем пароль
            self.plainPassword.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            # скрываем пароль
            self.plainPassword.setEchoMode(QtWidgets.QLineEdit.Password)

    def switchWindow(self):
        print("click!")

        # получение логина и пароля 
        login = self.plainLogin.text()
        password = self.plainPassword.text()
        
        if not login or not password:
            return
        
        if self.db.checkUser(login, password):
            # очистка полей 

            user_name = self.db.getName(login, password)

            self.plainLogin.clear()
            self.plainPassword.clear()
            self.ShowPasswordCheckBox.setChecked(False)
            self.plainPassword.setEchoMode(QtWidgets.QLineEdit.Password)
            
            QMessageBox.information(self, "Успешный вход", "Вход выполнен успешно.")

            self.hide()
            if self._window2 is None:
                self._window2 = Workspace(self, user_name)
            self._window2.show()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверный логин или пароль!\nПопробуйте еще раз.")
            self.plainPassword.clear()

        # проверка полей
        print(login, password)

class Workspace(QtWidgets.QMainWindow, workspace.Ui_MainWindow):
    def __init__(self, window1 = None, user_name=None, window3 = None):
        super().__init__()
        self.setupUi(self)

        self.WelcomText.setText(f"Добро пожаловать, {user_name}!")
        self.WelcomText.setStyleSheet("font-size: 18px;")

        # ожидает нажатия, а после запускает смену окна
        self.ExitButton.clicked.connect(self.switchWindow1)
        self._window1 = window1
        self.GetMaterial.clicked.connect(self.switchWindow2)
        self._window3 = window3

    def switchWindow1(self):
        self.hide()
        if self._window1 is None:
            self._window1 = Autorization(self)
        self._window1.show()

    def switchWindow2(self):
        self.hide()
        if self._window3 is None:
            self._window3 = Analysis(self)
        self._window3.show()   

class Analysis(QtWidgets.QMainWindow, analizes.Ui_MainWindow):
    def __init__(self, window1 = None):
        super().__init__()
        self.setupUi(self)

        # ожидает нажатия, а после запускает смену окна

        self.createZakaz.clicked.connect(self.switchWindowCreate)
        self._window1 = window1
        self.cancelZakaz.clicked.connect(self.switchWindowCancel)
        self._window1 = window1

    def switchWindowCreate(self):
        self.hide()
        if self._window1 is None:
            self._window1 = Workspace(self)
        self._window1.show()
        

    def switchWindowCancel(self):
        self.hide()
        if self._window1 is None:
            self._window1 = Workspace(self)
        self._window1.show()    

     


def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = Autorization()  
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':  
    main()