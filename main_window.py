from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from config import Config
from scroll_label_widget import ScrollLabelWidget
from encryption_type_widget import EncryptionTypeWidget
from theme import Theme


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.user_name = "Szymon"
        # messages to show
        self.messages = []

        self.setWindowTitle("bsk-1 ")
        # setting geometry
        self.setGeometry(20, 20, 600, 400)

        # creating widgets
        self.scroll_label = ScrollLabelWidget(self)
        self.text_input = QLineEdit(self)
        self.encryption_type_widget = EncryptionTypeWidget(self, 20, 230)

        # setting widgets
        self.add_scrollable_list(self.scroll_label)
        self.add_input_text(self.text_input)

        # socket timer
        self.timer = QtCore.QTimer()
        self.start_socket_timer(self.timer)

        # showing all the widgets
        self.show()

    def add_scrollable_list(self, scroll_label):
        scroll_label.set_text("")
        scroll_label.setGeometry(20, 20, 560, 200)

    def add_input_text(self, text_input):
        text_input.setGeometry(20, 300, 400, 40)
        text_input.returnPressed.connect(self.did_enter_text_message)

    def did_enter_text_message(self):
        message = self.text_input.text()
        # empty message
        if not message:
            return
        self.text_input.clear()
        self.add_message(self.user_name, message, Config.user_text_color())

    def add_message(self, username, message, color):
        message = Theme.color_it(username + ': ', color) + \
                  Theme.color_it(message, Config.text_color()) + \
                  Theme.new_line()

        self.messages.append(message)
        self.scroll_label.set_text(''.join(self.messages))

    def start_socket_timer(self, timer):
        timer.timeout.connect(self.did_tick)
        timer.start(Config.socket_interval())

    def did_tick(self):
        # TODO
        # add socket
        print("did tick")
