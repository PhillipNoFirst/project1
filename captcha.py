import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from pyqtcaptcha import Captcha, CaptchaDifficulty

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создание CAPTCHA виджета
        self.captcha = Captcha()
        self.captcha.setDifficulty(CaptchaDifficulty.MEDIUM)  # EASY, MEDIUM, HARD
        self.captcha.setFixedSize(200, 50)
        
        # Поле для ввода
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите код с картинки")
        
        # Кнопка проверки
        self.check_button = QPushButton("Проверить")
        self.check_button.clicked.connect(self.verify_captcha)
        
        # Метка для результата
        self.result_label = QLabel("")
        
        layout.addWidget(self.captcha)
        layout.addWidget(self.input_field)
        layout.addWidget(self.check_button)
        layout.addWidget(self.result_label)
    
    def verify_captcha(self):
        user_input = self.input_field.text()
        if self.captcha.validate(user_input):
            self.result_label.setText("✓ CAPTCHA решена верно!")
            self.result_label.setStyleSheet("color: green;")
        else:
            self.result_label.setText("✗ Неверный код. Попробуйте снова.")
            self.result_label.setStyleSheet("color: red;")
            self.captcha.refresh()  # Обновить CAPTCHA
            self.input_field.clear()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())