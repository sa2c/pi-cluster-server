from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys, time, os
import numpy as np
from display.leaderboard import LeaderboardWidget
from display.pyside_dynamic import loadUiWidget
from display.activity_monitor import ActivityPlotter
from display.matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot

script_directory = os.path.dirname(os.path.abspath(__file__))


class ResultsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = loadUiWidget(
            os.path.join(script_directory, '../designer/results.ui'),
            customWidgets=[
                LeaderboardWidget, PlotCanvas
            ])
        self.setCentralWidget(self.ui)

        self.image_index = 0
        self.run_queue = []
        self.currently_shown_simulation = None

        # cycle simulation image every 5ms seconds (for video effect)
        timer = QTimer(self)
        timer.timeout.connect(self.update_simulation_views)
        timer.start(5)

    def switch_to_simulation_view(self, simulation):
        self.currently_shown_simulation = simulation
        self.update_simulation_views()

    def update_simulation_views(self):
        ntimesteps = 10

        # clear screen
        self.ui.left_view.figure.clear()
        self.ui.right_view.figure.clear()

        if not self.currently_shown_simulation is None:
            image = self.currently_shown_simulation['rgb']

            vtk_file = run_filepath(self.currently_shown_simulation['index'],
                                    f'elmeroutput{self.image_index:04}.vtk')
            print(f'reading vtk file {vtk_file}')

            if self.image_index > 0:
                vtk_to_plot(self.ui.left_view, vtk_file, 16, False, True,
                            False, image)
                vtk_to_plot(self.ui.right_view, vtk_file, 16, True, False,
                            True, None)

            self.image_index = (self.image_index + 1) % (ntimesteps + 1)

    def set_currently_shown_simulation(self, index):
        datafile = run_filepath(index, 'simulation.npy')
        self.currently_shown_simulation = np.load(datafile)

    def simulations_changed(self, simulations):
        self.ui.leaderboard.update(simulations)
