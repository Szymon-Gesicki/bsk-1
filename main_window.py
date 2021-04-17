from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from connection.client_stream import ClientStream
from connection.host_stream import HostStream
from config import Config
from scroll_label_widget import ScrollLabelWidget
from encryption_type_widget import EncryptionTypeWidget
from theme import Theme
from aes_cipher import AESCipher
import random


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.user_name = "me"
        # messages to show
        self.messages = []

        # initialize connection
        self.stream = ClientStream()
        # self.stream = HostStream()

        self.setWindowTitle("secret messenger")
        # setting geometry
        self.setGeometry(20, 20, 600, 400)

        # creating widgets
        self.scroll_label = ScrollLabelWidget(self)
        self.text_input = QLineEdit(self)
        self.encryption_type_widget = EncryptionTypeWidget(self, 20, 230, AESCipher.AVAILABLE_MODES)
        self.file_button = QPushButton(self)
        self.connection_button = QPushButton(self)

        # setting widgets
        self.add_scrollable_list()
        self.add_input_text()
        self.add_file_button()
        self.add_connection_button()

        # socket timer
        self.timer = QtCore.QTimer()
        self.start_socket_timer()

        # showing all the widgets
        self.show()

    def add_scrollable_list(self):
        self.scroll_label.set_text("")
        self.scroll_label.setGeometry(20, 20, 560, 200)

    def add_input_text(self):
        self.text_input.setGeometry(20, 300, 400, 40)
        self.text_input.returnPressed.connect(self.did_enter_text_message)

    def did_enter_text_message(self):
        message = self.text_input.text()
        # empty message
        if not message:
            return
        self.text_input.clear()
        if not self.stream.send_message(message):
            self.add_message('system', 'error while sending message', Config.system_text_color())
        else:
            self.add_message(self.user_name, message, Config.user_text_color())

    def add_file_button(self):
        self.file_button.setGeometry(420, 300, 80, 40)
        self.file_button.setText('send file')
        self.file_button.clicked.connect(self.did_press_file_button)

    def add_connection_button(self):
        self.connection_button.setGeometry(510, 300, 80, 40)
        self.connection_button.setText('connect')
        self.connection_button.clicked.connect(self.did_press_connection_button)

    def add_message(self, username, message, color):
        message = Theme.colorize(username + ': ', color) + \
                  Theme.colorize(message, Config.text_color()) + \
                  Theme.new_line()

        self.messages.append(message)
        self.scroll_label.set_text(''.join(self.messages))

    def did_press_file_button(self):
        file = QFileDialog.getOpenFileUrl(self, 'select file to send')
        if not file[0].isEmpty():
            self.add_message('system', 'sending file: "' + str(file[0].fileName()) + '"', Config.system_text_color())
        # TODO
        # send file

    def did_press_connection_button(self):
        if self.stream.connect():
            self.add_message('system', 'did connect', Config.system_text_color())
        else:
            self.add_message('system', 'error while connecting', Config.system_text_color())

    def start_socket_timer(self):
        self.timer.timeout.connect(self.did_tick)
        self.timer.start(Config.socket_interval())

    def did_change_encryption_mode(self, mode):
        print("did_change_encryption_mode " + str(mode))

    def did_tick(self):
        messages = self.stream.get_new_messages()
        for m in messages:
            self.add_message('stranger', m, Config.strangers_text_color())

