from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import simulation_proxy
import time
import numpy as np
import settings


class ClusterNotifyThread(QThread):
    simulations_changed = Signal(dict)

    def run(self):
        while True:
            ids = simulation_proxy.fetch_max_drag(settings.leaderboard_number)

            simulations = [simulation_proxy.load_simulation(id) for id in ids]

            self.simulations_changed.emit(simulations)
            time.sleep(1)
