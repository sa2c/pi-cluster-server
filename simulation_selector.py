from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from cluster_run import run_filepath, all_available_indices_and_names, load_simulation, load_simulation_name
import numpy as np


class SimulationSelector(QListWidget):

    simulation_view_changed = Signal(dict)
    viewfinder_view_selected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.simulation_indices = all_available_indices_and_names()
        self.redraw_items()

        # connect signal
        self.currentRowChanged.connect(self.current_row_changed)

    def simulation_finished_action(self, index):
        name = load_simulation_name(index)
        self.simulation_indices.insert(0, [index, name])
        self.redraw_items()

    def redraw_items(self):
        self.clear()

        item = QListWidgetItem('Viewfinder', self)
        self.addItem(item)

        for sim in self.simulation_indices:
            index = sim[0]
            name = sim[1]
            label = f'{ str(name) } ({ index })'
            item = QListWidgetItem(label, self)
            self.addItem(item)

    def current_row_changed(self, current_row):
        if current_row == 0:
            self.viewfinder_view_selected.emit()
        elif len(self.simulation_indices) > current_row - 1:
            index = self.simulation_indices[current_row - 1][0]
            simulation = load_simulation(index)

            self.simulation_view_changed.emit(simulation)
        else:
            print(f'index {current_row - 1} > simulation_indicies length')

    def set_to_viewfinder(self):
        self.setCurrentRow(0)


if __name__ == '__main__':
    import sys
    app = QApplication()
    s = SimulationSelector()

    def echo_sim(sim):
        print(sim)

    def echo_viewfinder():
        print('viewfinder')

    s.simulation_view_changed.connect(echo_sim)
    s.viewfinder_view_selected.connect(echo_viewfinder)

    s.show()

    sys.exit(app.exec_())
