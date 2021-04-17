from PyQt5.QtWidgets import *


class EncryptionTypeWidget:

    WIDTH = 80
    HEIGHT = 40

    def __init__(self, window, start_x, start_y, values):
        self.window = window
        self.values = values

        for idx, value in enumerate(self.values, 0):
            if idx == 0:
                self.window.did_change_encryption_mode(value)
            self.add_button(self.values[value], start_x + idx * self.WIDTH, start_y, idx == 0)

    def add_button(self, button_name, x, y, is_selected):
        radio_button = QRadioButton(button_name, self.window)
        radio_button.setChecked(is_selected)
        radio_button.setGeometry(x, y, self.WIDTH, self.HEIGHT)
        radio_button.toggled.connect(lambda: self.radio_button_state(radio_button))

    def radio_button_state(self, radio_button):
        if radio_button.isChecked():
            mode = self.mode_from_value(radio_button.text())
            self.window.did_change_encryption_mode(mode)

    def mode_from_value(self, value):
        return list(self.values.keys())[list(self.values.values()).index(value)]






