import sys
import sqlite3
import hashlib
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QStackedWidget, QDialog, QFormLayout, QComboBox, QInputDialog)


# Хеширование паролей
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("airline_system.db")
    cursor = conn.cursor()

    # Таблицы базы данных
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
                        id INTEGER PRIMARY KEY,
                        flight_number TEXT NOT NULL,
                        departure TEXT NOT NULL,
                        arrival TEXT NOT NULL,
                        date TEXT NOT NULL,
                        seats_available INTEGER NOT NULL,
                        price REAL NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        flight_id INTEGER NOT NULL,
                        passenger_name TEXT NOT NULL,
                        payment_status TEXT NOT NULL,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(flight_id) REFERENCES flights(id)
                    )''')

    conn.commit()
    conn.close()


class LoginWindow(QWidget):
    def __init__(self, stack_widget):
        super().__init__()
        self.stack_widget = stack_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.username_input.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setStyleSheet("font-size: 14px;")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Войти", self)
        login_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        register_button = QPushButton("Зарегистрироваться", self)
        register_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        register_button.clicked.connect(self.open_register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = hash_password(self.password_input.text())

        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Успех", "Вы вошли в систему!")
            if user[1] == "Администратор":
                self.stack_widget.parent().set_admin_mode()
            else:
                self.stack_widget.parent().set_user_mode()
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильный логин или пароль!")

    def open_register(self):
        self.stack_widget.setCurrentIndex(2)


class RegisterWindow(QWidget):
    def __init__(self, stack_widget):
        super().__init__()
        self.stack_widget = stack_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.role_input = QComboBox(self)
        self.role_input.addItems(["Клиент", "Администратор"])
        self.role_input.setStyleSheet("background-color: #bdd1eb")
        layout.addWidget(self.role_input)

        register_button = QPushButton("Зарегистрироваться", self)
        register_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        back_button = QPushButton("Назад", self)
        back_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = hash_password(self.password_input.text())
        role = self.role_input.currentText()

        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.go_back()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такой пользователь уже существует!")
        conn.close()

    def go_back(self):
        self.stack_widget.setCurrentIndex(0)


class FlightManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.flights_table = QTableWidget()
        layout.addWidget(self.flights_table)

        refresh_button = QPushButton("Обновить рейсы")
        refresh_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        refresh_button.clicked.connect(self.load_flights)
        layout.addWidget(refresh_button)

        add_flight_button = QPushButton("Добавить рейс")
        add_flight_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        add_flight_button.clicked.connect(self.open_add_flight_dialog)
        layout.addWidget(add_flight_button)

        self.setLayout(layout)

    def load_flights(self):
        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, flight_number, departure, arrival, date, seats_available, price FROM flights")
        flights = cursor.fetchall()
        conn.close()

        self.flights_table.setRowCount(len(flights))
        self.flights_table.setColumnCount(7)
        self.flights_table.setHorizontalHeaderLabels(
            ["ID", "Рейс", "Откуда", "Куда", "Дата", "Места", "Цена"]
        )

        for row, flight in enumerate(flights):
            for col, data in enumerate(flight):
                self.flights_table.setItem(row, col, QTableWidgetItem(str(data)))

    def open_add_flight_dialog(self):
        dialog = AddFlightDialog()
        dialog.exec()
        self.load_flights()


class AddFlightDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить рейс")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.flight_number_input = QLineEdit(self)
        layout.addRow("Номер рейса:", self.flight_number_input)

        self.departure_input = QLineEdit(self)
        layout.addRow("Откуда:", self.departure_input)

        self.arrival_input = QLineEdit(self)
        layout.addRow("Куда:", self.arrival_input)

        self.date_input = QLineEdit(self)
        layout.addRow("Дата (ГГГГ-ММ-ДД):", self.date_input)

        self.seats_input = QLineEdit(self)
        layout.addRow("Места:", self.seats_input)

        self.price_input = QLineEdit(self)
        layout.addRow("Цена:", self.price_input)

        add_button = QPushButton("Добавить")
        add_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        add_button.clicked.connect(self.add_flight)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_flight(self):
        flight_number = self.flight_number_input.text()
        departure = self.departure_input.text()
        arrival = self.arrival_input.text()
        date = self.date_input.text()
        seats = self.seats_input.text()
        price = self.price_input.text()

        if not all([flight_number, departure, arrival, date, seats, price]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO flights (flight_number, departure, arrival, date, seats_available, price) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (flight_number, departure, arrival, date, seats, price)
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Рейс добавлен!")
        self.close()


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система продажи авиабилетов")

        self.stack_widget = QStackedWidget()
        self.setCentralWidget(self.stack_widget)

        self.login_window = LoginWindow(self.stack_widget)
        self.register_window = RegisterWindow(self.stack_widget)
        self.flight_management_window = FlightManagementWindow()

        self.stack_widget.addWidget(self.login_window)
        self.stack_widget.addWidget(self.flight_management_window)
        self.stack_widget.addWidget(self.register_window)

    def set_admin_mode(self):
        self.stack_widget.setCurrentWidget(self.flight_management_window)
        self.flight_management_window.load_flights()

    def set_user_mode(self):
        QMessageBox.information(self, "Ошибка", "Вход только для администраторов.")


class FlightBookingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.flights_table = QTableWidget()
        layout.addWidget(self.flights_table)

        book_button = QPushButton("Забронировать рейс")
        book_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        book_button.clicked.connect(self.book_flight)
        layout.addWidget(book_button)

        self.setLayout(layout)
        self.load_flights()

    def load_flights(self):
        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, flight_number, departure, arrival, date, seats_available, price FROM flights")
        flights = cursor.fetchall()
        conn.close()

        self.flights_table.setRowCount(len(flights))
        self.flights_table.setColumnCount(7)
        self.flights_table.setHorizontalHeaderLabels(
            ["ID", "Рейс", "Откуда", "Куда", "Дата", "Места", "Цена"]
        )

        for row, flight in enumerate(flights):
            for col, data in enumerate(flight):
                self.flights_table.setItem(row, col, QTableWidgetItem(str(data)))

    def book_flight(self):
        selected_row = self.flights_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите рейс для бронирования!")
            return

        flight_id = self.flights_table.item(selected_row, 0).text()
        passenger_name, ok = QInputDialog.getText(self, "Введите имя пассажира", "Имя:")

        if ok and passenger_name:
            conn = sqlite3.connect("airline_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT seats_available FROM flights WHERE id = ?", (flight_id,))
            seats_available = cursor.fetchone()[0]

            if seats_available > 0:
                cursor.execute(
                    "INSERT INTO bookings (user_id, flight_id, passenger_name, payment_status) VALUES (?, ?, ?, ?)",
                    (1, flight_id, passenger_name, "paid"))  # Здесь user_id = 1 для примера
                cursor.execute("UPDATE flights SET seats_available = seats_available - 1 WHERE id = ?", (flight_id,))
                conn.commit()
                QMessageBox.information(self, "Успех", "Рейс забронирован!")
            else:
                QMessageBox.warning(self, "Ошибка", "Нет доступных мест на рейс!")
            conn.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Имя пассажира не может быть пустым!")


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система продажи авиабилетов")

        self.stack_widget = QStackedWidget()
        self.setCentralWidget(self.stack_widget)

        self.login_window = LoginWindow(self.stack_widget)
        self.register_window = RegisterWindow(self.stack_widget)
        self.flight_management_window = FlightManagementWindow()
        self.flight_booking_window = FlightBookingWindow()

        self.stack_widget.addWidget(self.login_window)
        self.stack_widget.addWidget(self.flight_management_window)
        self.stack_widget.addWidget(self.register_window)
        self.stack_widget.addWidget(self.flight_booking_window)

    def set_admin_mode(self):
        self.stack_widget.setCurrentWidget(self.flight_management_window)
        self.flight_management_window.load_flights()

    def set_user_mode(self):
        self.stack_widget.setCurrentWidget(self.flight_booking_window)
        self.flight_booking_window.load_flights()


class PassengerManagementWindow(QWidget):
    def __init__(self, flight_id):
        super().__init__()
        self.flight_id = flight_id

        # Создание интерфейса
        layout = QVBoxLayout()

        self.passengers_table = QTableWidget()
        layout.addWidget(self.passengers_table)

        refresh_button = QPushButton("Обновить пассажиров")
        refresh_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        refresh_button.clicked.connect(self.load_passengers)
        layout.addWidget(refresh_button)

        self.setLayout(layout)
        self.load_passengers()

    def load_passengers(self):
        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT b.passenger_name, b.payment_status 
                          FROM bookings b 
                          WHERE b.flight_id = ?''', (self.flight_id,))
        passengers = cursor.fetchall()
        conn.close()

        self.passengers_table.setRowCount(len(passengers))
        self.passengers_table.setColumnCount(2)
        self.passengers_table.setHorizontalHeaderLabels(
            ["Имя пассажира", "Статус оплаты"]
        )

        for row, passenger in enumerate(passengers):
            for col, data in enumerate(passenger):
                self.passengers_table.setItem(row, col, QTableWidgetItem(str(data)))


class FlightManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.flights_table = QTableWidget()
        layout.addWidget(self.flights_table)

        refresh_button = QPushButton("Обновить рейсы")
        refresh_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        refresh_button.clicked.connect(self.load_flights)
        layout.addWidget(refresh_button)

        add_flight_button = QPushButton("Добавить рейс")
        add_flight_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        add_flight_button.clicked.connect(self.open_add_flight_dialog)
        layout.addWidget(add_flight_button)

        view_passengers_button = QPushButton("Просмотреть пассажиров")
        view_passengers_button.setStyleSheet("background-color: #9ebee8; font-size: 14px;")
        view_passengers_button.clicked.connect(self.open_passenger_management)
        layout.addWidget(view_passengers_button)

        self.setLayout(layout)

        self.load_flights()

    def load_flights(self):
        conn = sqlite3.connect("airline_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, flight_number, departure, arrival, date, seats_available, price FROM flights")
        flights = cursor.fetchall()
        conn.close()

        self.flights_table.setRowCount(len(flights))
        self.flights_table.setColumnCount(7)
        self.flights_table.setHorizontalHeaderLabels(
            ["ID", "Рейс", "Откуда", "Куда", "Дата", "Места", "Цена"]
        )

        for row, flight in enumerate(flights):
            for col, data in enumerate(flight):
                self.flights_table.setItem(row, col, QTableWidgetItem(str(data)))

    def open_passenger_management(self):
        selected_row = self.flights_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите рейс для просмотра пассажиров!")
            return

        flight_id = self.flights_table.item(selected_row, 0).text()
        self.passenger_management_window = PassengerManagementWindow(flight_id)
        self.passenger_management_window.setWindowTitle(f"Пассажиры на рейс {flight_id}")
        self.passenger_management_window.show()

    def open_add_flight_dialog(self):
        dialog = AddFlightDialog()
        dialog.exec()
        self.load_flights()


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система продажи авиабилетов")

        self.stack_widget = QStackedWidget()
        self.setCentralWidget(self.stack_widget)

        self.login_window = LoginWindow(self.stack_widget)
        self.register_window = RegisterWindow(self.stack_widget)
        self.flight_management_window = FlightManagementWindow()
        self.flight_booking_window = FlightBookingWindow()

        self.stack_widget.addWidget(self.login_window)
        self.stack_widget.addWidget(self.flight_management_window)
        self.stack_widget.addWidget(self.register_window)
        self.stack_widget.addWidget(self.flight_booking_window)

    def set_admin_mode(self):
        self.stack_widget.setCurrentWidget(self.flight_management_window)
        self.flight_management_window.load_flights()

    def set_user_mode(self):
        self.stack_widget.setCurrentWidget(self.flight_booking_window)
        self.flight_booking_window.load_flights()


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
