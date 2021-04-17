from PyQt5.QtWidgets import *


class EncryptionTypeWidget:

    width = 80
    height = 40

    def __init__(self, window, start_x, start_y):
        self.window = window
        # Todo
        # add encryption type class
        self.add_button('type1', start_x, start_y, True)
        self.add_button('type2', start_x + self.width, start_y, False)
        self.add_button('type3', start_x + 2*self.width, start_y, False)

    def add_button(self, button_name, x, y, is_selected):
        radio_button = QRadioButton(button_name, self.window)
        radio_button.setChecked(is_selected)
        radio_button.setGeometry(x, y, self.width, self.height)
        radio_button.toggled.connect(lambda: self.radio_button_state(radio_button))

    def radio_button_state(self, radio_button):
        # TODO
        pass




