from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from leaderboard import LeaderboardWidget
from video_capture import QVideoWidget
from pyside_dynamic import loadUi
from matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ViewfinderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(
            os.path.join(SCRIPT_DIRECTORY, 'designer/viewfinder.ui'),
            self,
            customWidgets={
                'QVideoWidget': QVideoWidget,
                'LeaderboardWidget': LeaderboardWidget,
                'PlotCanvas': PlotCanvas
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation_views)
        self.timer.start(5)

    def set_simulation(self, index):
        self.image_index = 0
        self.update_simulation_views()
        self.switch_stack(1)

    def switch_stack(self, index):
        self.leftStack.setCurrentIndex(index)
        self.rightStack.setCurrentIndex(index)

    def update_simulation_views(self):
        if self.leftStack.currentIndex() == 0:
            return

        vtk_file = f'outbox/testrun1/elmeroutput000{self.image_index + 1}.vtk'
        imagefile = 'outbox/testrun1/kinect/scf1-fullcolorimage.png'

        self.left_view.figure.clear()
        self.right_view.figure.clear()

        vtk_to_plot(self.left_view, vtk_file, 1, False, True, False, imagefile)
        vtk_to_plot(self.right_view, vtk_file, 1, True, False, True, None)

        self.image_index = (self.image_index + 1) % 8


def main():
    app = QApplication(sys.argv)
    window = ViewfinderDialog()
    window.set_simulation(1)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
