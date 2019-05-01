from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from display.pyside_dynamic import loadUi

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ColorCalibration(QDialog):

    color_changed = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(
            os.path.join(SCRIPT_DIRECTORY, '../designer/color_calibrate.ui'),
            self)

        self.red.valueChanged.connect(self._color_changed)
        self.green.valueChanged.connect(self._color_changed)
        self.blue.valueChanged.connect(self._color_changed)

    def _color_changed(self):
        r = self.red.value()
        g = self.green.value()
        b = self.blue.value()

        self.red_txt.setText(str(r))
        self.green_txt.setText(str(g))
        self.blue_txt.setText(str(b))

        self.color_changed.emit((r / 100, g / 100, b / 100))


def main():
    app = QApplication(sys.argv)
    window = ColorCalibration()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
