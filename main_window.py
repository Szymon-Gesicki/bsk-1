from PyQt5.QtWidgets import *
from PyQt5 import QtCore
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

        self.setWindowTitle("secret messenger")
        # setting geometry
        self.setGeometry(20, 20, 600, 400)

        # creating widgets
        self.scroll_label = ScrollLabelWidget(self)
        self.text_input = QLineEdit(self)
        self.encryption_type_widget = EncryptionTypeWidget(self, 20, 230, AESCipher.AVAILABLE_MODES)
        self.file_button = QPushButton(self)

        # setting widgets
        self.add_scrollable_list()
        self.add_input_text()
        self.add_file_button()

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
        self.add_message(self.user_name, message, Config.user_text_color())

    def add_file_button(self):
        self.file_button.setGeometry(450, 300, 80, 40)
        self.file_button.setText('send file')
        self.file_button.clicked.connect(self.did_press_file_button)

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

    def start_socket_timer(self):
        self.timer.timeout.connect(self.did_tick)
        self.timer.start(Config.socket_interval())

    def did_change_encryption_mode(self, mode):
        print("did_change_encryption_mode " + str(mode))

    def did_tick(self):
        if random.randint(0, 10) == 1:
            self.add_message('stranger', 'message form stranger', Config.strangers_text_color())


