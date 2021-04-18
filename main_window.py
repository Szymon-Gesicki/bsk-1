from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from connection.client_stream import ClientStream, NotificationType
from connection.host_stream import HostStream
from config import Config
from scroll_label_widget import ScrollLabelWidget
from encryption_type_widget import EncryptionTypeWidget
from theme import Theme
from aes_cipher import AESCipher


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.user_name = "me"
        # messages to show
        self.messages = []

        # initialize connection
        self.stream = None

        self.setWindowTitle("secret messenger")
        # setting geometry
        self.setGeometry(20, 20, 620, 400)

        # creating widgets
        self.scroll_label = ScrollLabelWidget(self)
        self.text_input = QLineEdit(self)
        self.encryption_type_widget = EncryptionTypeWidget(self, 20, 230, AESCipher.AVAILABLE_MODES)
        self.file_button = QPushButton(self)
        self.join_button = QPushButton(self)
        self.create_button = QPushButton(self)

        # setting widgets
        self.add_scrollable_list()
        self.add_input_text()
        self.add_file_button()
        self.add_join_button()
        self.add_create_button()

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

        if not self.stream:
            self.add_message('system', 'connect before send', Config.system_text_color())
        elif not self.stream.send_message(message):
            self.add_message('system', 'error while sending message', Config.system_text_color())
        else:
            self.add_message(self.user_name, message, Config.user_text_color())

    def add_file_button(self):
        self.file_button.setGeometry(420, 300, 60, 40)
        self.file_button.setText('file')
        self.file_button.clicked.connect(self.did_press_file_button)

    def add_create_button(self):
        self.create_button.setGeometry(540, 300, 70, 40)
        self.create_button.setText('create')
        self.create_button.clicked.connect(self.did_press_create_button)

    def add_join_button(self):
        self.join_button.setGeometry(480, 300, 60, 40)
        self.join_button.setText('join')
        self.join_button.clicked.connect(self.did_press_join_button)

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
            self.stream.send_file(file[0].path())

    def did_press_join_button(self):
        self.stream = ClientStream()
        self.disable_stream_button()
        if self.stream.connect():
            self.add_message('system', 'did connect', Config.system_text_color())
        else:
            self.enable_stream_button()
            self.stream = None
            self.add_message('system', 'error while connecting', Config.system_text_color())

    def did_press_create_button(self):
        self.disable_stream_button()
        self.stream = HostStream()

    def disable_stream_button(self):
        self.join_button.setEnabled(False)
        self.create_button.setEnabled(False)

    def enable_stream_button(self):
        self.join_button.setEnabled(True)
        self.create_button.setEnabled(True)

    def start_socket_timer(self):
        self.timer.timeout.connect(self.did_tick)
        self.timer.start(Config.socket_interval())

    def did_change_encryption_mode(self, mode):
        print("did_change_encryption_mode " + str(mode))

    def did_tick(self):
        if not self.stream:
            return
        messages = self.stream.get_new_notifications()
        for m in messages:
            if m['type'] == NotificationType.MESSAGE:
                self.add_message('stranger', m['message'], Config.strangers_text_color())

            elif m['type'] == NotificationType.RECEIVING_FILE:
                self.add_message('stranger', 'processed: ' + str(m['processed']) + ' size: ' + str(m['size']), Config.strangers_text_color())

            elif m['type'] == NotificationType.SENDING_FILE:
                self.add_message(self.user_name, 'processed: ' + str(m['processed']) + ' size: ' + str(m['size']), Config.strangers_text_color())
