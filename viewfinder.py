from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from leaderboard import LeaderboardWidget
from video_capture import QVideoWidget
from pyside_dynamic import loadUi

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ViewfinderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(
            os.path.join(SCRIPT_DIRECTORY, 'designer/viewfinder.ui'),
            self,
            customWidgets={
                'QVideoWidget': QVideoWidget,
                'LeaderboardWidget': LeaderboardWidget
            })


def main():
    app = QApplication(sys.argv)
    window = ViewfinderDialog()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
