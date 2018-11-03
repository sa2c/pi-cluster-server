from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class DetailForm(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.name = QLineEdit()
        self.name.setText('Simulation')
        self.email = QLineEdit()
        self.layout().addWidget(QLabel('name'))
        self.layout().addWidget(self.name)
        self.layout().addWidget(QLabel('email'))
        self.layout().addWidget(self.email)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok
                                        | QDialogButtonBox.Cancel)
        self.layout().addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.callback = parent.name_changed_action

        self.name.textChanged.connect(self.change_details)
        self.email.textChanged.connect(self.change_details)

    def change_details(self):
        self.callback(self.name.text(), self.email.text())
