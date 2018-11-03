
import sys
import os
import numpy as np
import time
import sys, random
from fabric import Connection

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
 
 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
 
import random



# gets the CPU usage information for one node
def get_cpu_usage(num_nodes):
    global cpu_usage
    print("Gathering data from nodes \n")

    cluster_address = "pi@137.44.2.181"
    cluster = Connection(host=cluster_address,connect_kwargs={"password":"sa2cpi"})

    cpu_usage = cluster.run('''bash cpuloadinfo.sh''', hide=True).stdout
    print(cpu_usage)
    cpu_usage = list(float(cpu_usage[:,1]))
    #cpu_usage = 100.0*np.random.rand(num_nodes)

    return
###################################################
###################################################


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.title = 'CPU usage from all nodes'
        self.width = 500
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        m = PlotCanvas(self, width=5, height=4)
 
        self.show()
 
 
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()
 
    def plot(self):
        ax = self.figure.add_subplot(111)

        # gets the CPU usage from all the nodes and plots the data
        num_nodes  = 14
        global cpu_usage

        #cpu_usage_global = np.zeros((timeperiod,num_nodes), dtype=float)
        cpu_usage = np.zeros(num_nodes, dtype=float)

        get_cpu_usage(num_nodes)
        print(cpu_usage)

        time = np.linspace(1,num_nodes,num_nodes)
        ax.bar(time, cpu_usage)
        ax.set_xlabel("Node number")
        ax.set_ylabel("CPU usage (%)")
        self.draw()


#############################################
#############################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
