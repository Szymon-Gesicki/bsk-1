from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ScrollLabelWidget(QScrollArea):

    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        # making widget resizable
        self.setWidgetResizable(True)
        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)
        # vertical box layout
        lay = QVBoxLayout(content)
        # creating label
        self.label = QLabel(content)
        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # making label multi-line
        self.label.setWordWrap(True)
        # adding label to the layout
        lay.addWidget(self.label)

    def set_text(self, text):
        # setting text to the label
        self.label.setText(text)
        # always scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 10000)

