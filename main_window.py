from PyQt5.QtCore import QDir
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

        self.password = ""
        self.fetch_password()

        self.user_name = "me"
        # messages to show
        self.messages = []

        self.host = ""
        self.host_timer = None

        self.encryption_mode = None
        self.progress_dialog = None

        # initialize connection
        self.stream = None

        self.setWindowTitle("secret messenger")
        # setting geometry
        self.setGeometry(20, 20, 620, 400)

        # creating widgets
        self.scroll_label = ScrollLabelWidget(self)
        self.text_input = QLineEdit(self)
        self.encryption_type_widget = EncryptionTypeWidget(self, 20, 230, AESCipher.AVAILABLE_MODES)
        self.encryption_type_widget.set_enabled(False)
        self.file_button = QPushButton(self)
        self.file_button.setEnabled(False)
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

    def fetch_password(self):
        text, ok = QInputDialog.getText(None, "", "Password", QLineEdit.Password)
        if ok and text:
            self.password = text

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
        file = QFileDialog.getOpenFileName(self, 'select file to send')
        if file[0]:
            self.add_message('system', 'sending file: "' + str(file[0]) + '"', Config.system_text_color())
            path = QDir.toNativeSeparators(file[0])
            self.stream.send_file(path)

    def did_press_join_button(self):
        host, result = QInputDialog.getText(self, 'Host dialog', 'Enter host:')

        if not result:
            return

        self.stream = ClientStream(host=host, encryption_mode=self.encryption_mode, password=self.password)
        self.disable_stream_button()
        if self.stream.connect():
            self.add_message('system', 'Did connect', Config.system_text_color())
            self.encryption_type_widget.set_enabled(True)
            self.file_button.setEnabled(True)

        else:
            self.enable_stream_button()
            self.stream = None
            self.add_message('system', 'Error while connecting', Config.system_text_color())

    def did_press_create_button(self):
        host_name, result = QInputDialog.getText(self, 'Host dialog', 'Enter host:')

        if not result:
            return

        self.add_message('system', 'Waiting for strangers', Config.system_text_color())
        self.disable_stream_button()

        self.host = host_name
        # connection after a second to refresh the view
        self.host_timer = QtCore.QTimer()
        self.host_timer.timeout.connect(self.start_host)
        self.host_timer.start(1000)  # 1 second

    def start_host(self):
        self.host_timer.stop()
        self.create_host(self.host)
        self.add_message('system', 'Did connect', Config.system_text_color())
        self.encryption_type_widget.set_enabled(True)
        self.file_button.setEnabled(True)

    def create_host(self, host):
        self.stream = HostStream(host=host, encryption_mode=self.encryption_mode, password=self.password)

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
        self.encryption_mode = mode

        if self.stream:
            self.stream.set_encryption_mode(self.encryption_mode)

    def did_tick(self):
        if not self.stream:
            return

        messages = self.stream.get_new_notifications()

        for m in messages:
            if m['type'] == NotificationType.MESSAGE:
                self.add_message('stranger', m['message'], Config.strangers_text_color())

            elif m['type'] == NotificationType.RECEIVING_FILE:
                if m['finished']:
                    if self.progress_dialog:
                        self.progress_dialog.cancel()
                    self.add_message('system', 'file downloaded.', Config.system_text_color())
                else:
                    if not self.progress_dialog:
                        self.progress_dialog = QProgressDialog("Receiving file...", "Cancel", 0, m['size'], self)
                    else:
                        self.progress_dialog.setValue(m['processed'])

            elif m['type'] == NotificationType.SENDING_FILE:
                if m['finished']:
                    if self.progress_dialog:
                        self.progress_dialog.cancel()
                    self.add_message('system', 'file sent.', Config.system_text_color())
                else:
                    if not self.progress_dialog:
                        self.progress_dialog = QProgressDialog("Sending file...", "Cancel", 0, m['size'], self)
                    else:
                        self.progress_dialog.setValue(m['processed'])

            elif m['type'] == NotificationType.ENCRYPTION_MODE_CHANGE:
                self.encryption_mode = AESCipher.AVAILABLE_MODES[m['mode']]
                self.add_message('system', 'Stranger changed the encryption mode to ' + str(self.encryption_mode), Config.system_text_color())
                self.encryption_type_widget.change_value(self.encryption_mode)
