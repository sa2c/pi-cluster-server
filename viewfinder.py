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

        self.image_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation_views)
        self.timer.start(5)

        self.progress_slots = [self.slot1, self.slot2, self.slot3, self.slot4]
        self.indices_in_slots = [None, None, None, None]

    def switch_stack(self, index):
        self.leftStack.setCurrentIndex(index)
        self.rightStack.setCurrentIndex(index)

    def set_current_simulation_index(self, index):
        self.current_simulation_index = index
        self.image_index = 0
        self.update_simulation_views()
        self.switch_stack(1)

    def switch_to_viewfinder(self):
        self.switch_stack(0)

    def switch_to_simulation_view(self):
        self.switch_stack(1)

    def update_simulation_views(self):
        ntimesteps = 10
        if self.leftStack.currentIndex() == 0:
            return

        vtk_file = f'outbox/testrun1/elmeroutput{self.image_index:04}.vtk'
        imagefile = 'outbox/testrun1/kinect/scf1-fullcolorimage.png'

        self.left_view.figure.clear()
        self.right_view.figure.clear()

        if self.image_index > 0:
            vtk_to_plot(self.left_view, vtk_file, 1, False, True, False,
                        imagefile)
            vtk_to_plot(self.right_view, vtk_file, 1, True, False, True, None)

        self.image_index = (self.image_index + 1) % (ntimesteps + 1)

    def set_progress(self, index_run, progress):
        slot_number = self.indices_in_slots.index(index_run)
        self.progress_slots[slot_number].setValue(progress)

    def start_simulation(self, index_run, slot, name):
        # reset progress
        pbar = self.progress_slots[slot]
        pbar.setValue(0)
        pbar.setFormat(f'{name} : %p%')
        self.indices_in_slots[slot] = index_run

    def finish_simulation(self, index_run):
        slot_number = self.indices_in_slots.index(index_run)
        pbar = self.progress_slots[slot_number]
        pbar.setValue(0)
        self.indices_in_slots[slot_number] = None
        pbar.setFormat(f'Slot {slot_number} : %p%')

        self._start_drawing_result()


def main():
    app = QApplication(sys.argv)
    window = ViewfinderDialog()

    def finish_simulation():
        window.finish_simulation(15)
        window.finish_simulation(25)

    def update_progress():
        window.set_progress(15, 50)
        window.set_progress(25, 75)
        QTimer.singleShot(1000, finish_simulation)

    def start_simulation():
        window.start_simulation(15, 1, 'My Name')
        window.start_simulation(25, 2, 'Another Name')
        QTimer.singleShot(1000, update_progress)

    QTimer.singleShot(1000, start_simulation)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
