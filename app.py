import os
import sys
import threading
import asyncio
import telethon.errors
from PyQt6.QtCore import pyqtSignal
from telethon.sync import TelegramClient
from telethon import events

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMainWindow, QApplication, QLineEdit, QStyle, QInputDialog, QMessageBox
from PyQt6 import uic


import configparser


class App(QMainWindow):
    error_signal = pyqtSignal(str)

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.set()
        self.setWindowTitle('TelegramBot')

        if not os.path.exists('config.ini'):
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.write("[TELEGRAM]\n"
                        "API_ID =\n"
                        "api_hash =\n"
                        "auth_key =\n"
                        "phone_number =\n"
                        "destination =\n"
                        "chats =\n"
                        "key_words =")


        # actions
        self.ok_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.api_id_action = QAction(self.ok_icon, 'OK')
        self.api_hash_action = QAction(self.ok_icon, 'OK')
        self.destination_action = QAction(self.ok_icon, 'OK')
        self.chats_action = QAction(self.ok_icon, 'OK')
        self.keywords_action = QAction(self.ok_icon, 'OK')
        self.phone_action = QAction(self.ok_icon, 'OK')

        # api id
        self.api_id_ledit.addAction(self.api_id_action, QLineEdit.ActionPosition.TrailingPosition)
        self.api_id_action.setVisible(False)
        self.api_id_ledit.textChanged.connect(self.api_id_validation)

        # api hash
        self.api_hash_ledit.addAction(self.api_hash_action, QLineEdit.ActionPosition.TrailingPosition)
        self.api_hash_action.setVisible(False)
        self.api_hash_ledit.textChanged.connect(self.api_hash_validation)

        # destination
        self.destination_ledit.addAction(self.destination_action, QLineEdit.ActionPosition.TrailingPosition)
        self.destination_action.setVisible(False)
        self.destination_ledit.textChanged.connect(self.destination_validation)

        # chats
        self.chats_ledit.addAction(self.chats_action, QLineEdit.ActionPosition.TrailingPosition)
        self.chats_action.setVisible(False)
        self.chats_ledit.textChanged.connect(self.chats_validation)

        # keywords
        self.keywords_ledit.addAction(self.keywords_action, QLineEdit.ActionPosition.TrailingPosition)
        self.keywords_action.setVisible(False)
        self.keywords_ledit.textChanged.connect(self.keywords_validation)

        # phone number
        self.tel_num_ledit.addAction(self.phone_action, QLineEdit.ActionPosition.TrailingPosition)
        self.phone_action.setVisible(False)
        self.tel_num_ledit.textChanged.connect(self.phone_validation)

        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding='utf-8')
        self.config_parse()

        # login button
        self.login_btn.clicked.connect(self.login)

        # parsing button
        self.start_btn.clicked.connect(self.start_thread)

    def error(self, string: str):
        msg = QMessageBox(text=f'Error status:\n{string}', icon=QMessageBox.Icon.Critical)
        msg.setWindowTitle('Error')
        msg.exec()

    def set(self):
        uic.loadUi(self.resource_path('ui/mainwindow.ui'), self)
        self.setWindowIcon(QIcon(self.resource_path('ui/icons/telegram_logo_icon.ico')))
        self.show()

    def config_parse(self):
        if self.config["TELEGRAM"]["API_ID"]:
            self.api_id_ledit.setText(self.config["TELEGRAM"]["API_ID"])
            self.api_id_action.setVisible(True)
        if self.config["TELEGRAM"]["API_HASH"]:
            self.api_hash_ledit.setText(self.config["TELEGRAM"]["API_HASH"])
            self.api_hash_action.setVisible(True)
        if self.config["TELEGRAM"]["DESTINATION"]:
            self.destination_ledit.setText(self.config["TELEGRAM"]["DESTINATION"])
            self.destination_action.setVisible(True)
        if self.config["TELEGRAM"]["CHATS"]:
            self.chats_ledit.setText(self.config["TELEGRAM"]["CHATS"])
            self.chats_action.setVisible(True)
        if self.config["TELEGRAM"]["KEY_WORDS"]:
            self.keywords_ledit.setText(self.config["TELEGRAM"]["KEY_WORDS"])
            self.keywords_action.setVisible(True)
        if self.config["TELEGRAM"]["PHONE_NUMBER"]:
            self.tel_num_ledit.setText(self.config["TELEGRAM"]["PHONE_NUMBER"])
            self.phone_action.setVisible(True)

    def api_id_validation(self, val) -> bool:
        value = val
        if len(value) > 0:
            self.api_id_action.setVisible(True)
            return True
        else:
            self.api_id_action.setVisible(False)
            return False

    def api_hash_validation(self, val) -> bool:
        value = val
        if len(value) > 0:
            self.api_hash_action.setVisible(True)
            return True
        else:
            self.api_hash_action.setVisible(False)
            return False

    def destination_validation(self, val) -> bool:
        value = val
        if len(value) > 0:
            self.destination_action.setVisible(True)
            return True
        else:
            self.destination_action.setVisible(False)
            return False

    def chats_validation(self, val) -> bool:
        # tuple(val.split(', '))
        if len(val) > 0:
            self.chats_action.setVisible(True)
            return True
        else:
            self.chats_action.setVisible(False)
            return False

    def keywords_validation(self, val) -> bool:
        if len(val) > 0:
            self.keywords_action.setVisible(True)
            return True
        else:
            self.keywords_action.setVisible(False)
            return False

    def phone_validation(self, val) -> bool:
        if len(val) > 0:
            self.phone_action.setVisible(True)
            return True
        else:
            self.phone_action.setVisible(False)
            return False

    def login(self):
        """Connection to telegram"""
        try:
            bool_val = [self.api_id_action.isVisible(), self.api_hash_action.isVisible(),
                        self.destination_action.isVisible(), bool(self.chats_action.isVisible()),
                        bool(self.keywords_action.isVisible()), bool(self.phone_action.isVisible())
                        ]

            if all(bool_val):
                try:
                    self.config["TELEGRAM"]["API_ID"] = self.api_id_ledit.text()
                    self.config["TELEGRAM"]["API_HASH"] = self.api_hash_ledit.text()
                    self.config["TELEGRAM"]["DESTINATION"] = self.destination_ledit.text()
                    self.config["TELEGRAM"]["CHATS"] = self.chats_ledit.text()
                    self.config["TELEGRAM"]["KEY_WORDS"] = self.keywords_ledit.text()
                    self.config["TELEGRAM"]["PHONE_NUMBER"] = self.tel_num_ledit.text()
                    with open('config.ini', 'w', encoding='utf-8') as configfile:
                        self.config.write(configfile)
                    self.info_list.addItem('Запрос на подключение к Telegram отправлен')

                    self.client = self.init_telethon_client()
                    self.client.disconnect()
                    print('disconnected')
                except Exception as error:
                    self.info_list.addItem(f'Ошибка входa в аккаунт {error}')

            else:
                self.info_list.addItem('Необходимо заполнить все поля')
        except Exception as error:
            self.error_signal.emit(str(error))

    def init_telethon_client(self):
        """Initialization of telethon client"""
        try:
            client = TelegramClient('session', api_id=int(self.config["TELEGRAM"]["API_ID"]), api_hash=self.config["TELEGRAM"]["API_HASH"])
            client.connect()

            if not client.is_user_authorized():
                client.send_code_request(self.config["TELEGRAM"]["PHONE_NUMBER"])
                try:
                    auth_key, ok = QInputDialog.getText(self, "TelegramBot", "Введите код полученый в Telegram:")
                    if ok and len(auth_key) > 0:
                        self.info_list.addItem(f"Введенный код: {auth_key}")
                    client.sign_in(self.config["TELEGRAM"]["PHONE_NUMBER"], auth_key)
                    self.login_btn.setStyleSheet("background-color: rgb(40, 255, 7);")
                    self.login_btn.setText('Авторизация успешна')
                except telethon.errors.SessionPasswordNeededError:
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("TelegramBot")
                    dlg.setText("Отключите двухэтапную проверку в телеграм и повторите попытку авторизации")
                    dlg.show()
            else:
                self.login_btn.setStyleSheet("background-color: rgb(40, 255, 7);")
                self.login_btn.setEnabled(False)
                self.login_btn.setText('Авторизация успешна')
                self.info_list.addItem('Сессия найдена\n'
                                       'Авторизация успешна')

            return client
        except Exception as error:
            self.error_signal.emit(str(error))

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
         # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def start_thread(self):
        try:
            if self.start_btn.text() == 'Старт парсинга':
                self.thread = ParsingThread(self.config, self)
                self.thread.daemon=True
                self.thread.start()
                self.start_btn.setStyleSheet("background-color: rgb(40, 255, 7);")
                self.info_list.addItem('Парсер запущен')
                self.start_btn.setText('Остановить парсер')
            else:
                self.thread.stop()
                self.info_list.addItem('Парсер остановлен')
                self.start_btn.setText('Старт парсинга')
                self.start_btn.setStyleSheet("background-color: rgb(253, 253, 253);")
        except Exception as error:
            self.error_signal.emit(str(error))


class ParsingThread(threading.Thread):

    def __init__(self, config, main_window):
        super().__init__()
        self.loop = None
        self.config = config
        self.main_window = main_window
        self.client = None

    def stop(self):
        self.loop.stop()

    def run(self) -> None:
        chats_field = self.main_window.chats_ledit.text()
        keyword_field = self.main_window.keywords_ledit.text()
        destination_field = self.main_window.destination_ledit.text()
        key_words = keyword_field.replace(' ', '').split(',')
        chats = chats_field.replace(' ', '').split(',')
        chats_tuple = tuple(int(chat) if chat.isdigit() else chat for chat in chats)

        self.config["TELEGRAM"]["DESTINATION"] = self.main_window.destination_ledit.text()
        self.config["TELEGRAM"]["CHATS"] = self.main_window.chats_ledit.text()
        self.config["TELEGRAM"]["KEY_WORDS"] = self.main_window.keywords_ledit.text()
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

        destination = destination_field
        if destination.isdigit():
            destination = int(destination)
        else:
            destination = destination

        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.client = TelegramClient('session', api_id=int(self.config["TELEGRAM"]["API_ID"]),
                                    api_hash=self.config["TELEGRAM"]["API_HASH"])
            self.client.connect()

            print("Program is running...")

            @self.client.on(events.NewMessage(chats=chats_tuple))
            async def new_order(event):
                try:
                    print('Delivery new order...')
                    contain_key_word = False

                    for key_word in key_words:
                        if key_word.lower() in event.message.message.lower():
                            contain_key_word = True

                    if contain_key_word:
                        await self.client.forward_messages(destination, event.message)

                except Exception as error:
                    self.main_window.error_signal.emit(str(error))
                    print(f'Exception: {error}')

            # self.client.start()
            self.client.run_until_disconnected()
        except Exception as error:
            self.main_window.error_signal.emit(str(error))


if __name__ == "__main__":
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    ex = App(app)
    sys.exit(app.exec())
