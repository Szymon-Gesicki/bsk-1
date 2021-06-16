from PyQt5.QtWidgets import *
from aes_cipher import AESCipher


class EncryptionTypeWidget:

    WIDTH = 80
    HEIGHT = 40

    def __init__(self, window, start_x, start_y, values):
        self.window = window
        self.values = values
        self.radio_buttons = []
        self.disable = False

        for idx, value in enumerate(self.values, 0):
            if idx == 0:
                self.window.did_change_encryption_mode(value)
            self.add_button(self.values[value], start_x + idx * self.WIDTH, start_y, idx == 0)

    def add_button(self, button_name, x, y, is_selected):
        radio_button = QRadioButton(button_name, self.window)
        radio_button.setChecked(is_selected)
        radio_button.setGeometry(x, y, self.WIDTH, self.HEIGHT)
        radio_button.toggled.connect(lambda: self.radio_button_state(radio_button))
        self.radio_buttons.append(radio_button)

    def radio_button_state(self, radio_button):
        if self.disable:
            return

        if radio_button.isChecked():
            mode = AESCipher.mode_from_value(radio_button.text())
            self.window.did_change_encryption_mode(mode)

    def change_value(self, mode='test'):
        self.disable = True
        for button in self.radio_buttons:
            button.setAutoExclusive(False)
            button.setChecked(mode == button.text())
            button.setAutoExclusive(True)
        self.disable = False







