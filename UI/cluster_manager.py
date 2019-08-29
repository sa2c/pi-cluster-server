from PySide2.QtCore import *
import numpy as np
import os, io
import time
import requests
import tempfile
import errno
import datetime
import calendar
import requests

from settings import cluster_address

local_path = os.environ['PWD']

drags = np.empty((0,2))

def setup_cluster_inbox():
    with Connection(cluster_address) as cluster:
        try:
            cluster.sftp().stat(cluster_path+'/inbox')
        except IOError:
            cluster.sftp().mkdir(cluster_path+'/inbox')
            cluster.sftp().mkdir(cluster_path+'/signal_in')


def get_drag(index):
    print("Temporarily disabled")
    ## drag = compute_drag_for_simulation(index)

    ## simulation = load_simulation(index)
    ## simulation['score'] = drag
    ## simulation['index'] = index        
    ## save_simulation(simulation)        

    ##return drag
    return 10

def best_simulations(nsims):
    print("Needs to be re-implemented")
    global drags

    drag = np.array(drags)
    nsims = min(10, drag.shape[0])
    drag_sorted_indices = np.argsort(drag[:, 1])
    best_indices = drag[drag_sorted_indices[0:nsims], 0]

    simulations = [ load_simulation(int(i)) for index in best_indices ]

    return simulations


def simulation_postprocess(self, index):
    global drags

    drag = get_drag(index)
    drags = np.append(drags, np.array([[index, drag]]), axis = 0)

def dispatch_simulation(simulation):
    "Posts data to server to create a new run of a simulation"

    for key, val in simulation.items():
        if type(val) == np.ndarray:
            simulation[key] = val.tolist()

    response = requests.post(f'{cluster_address}/simulation', json=simulation)

    sim_id = response.json()['id']

    return sim_id


def load_simulation(index):
    # save simulation
    with open(run_filepath(index, 'simulation.npy'), 'rb') as file:
        return pickle.load(file)


def fetch_activity():
    response = requests.get(f'{cluster_address}/cluster/activity')
    cpu_usage = response.json()['cpu_usage']

    return cpu_usage

def get_run_completion_percentage(index):
    response = requests.post(f'{cluster_address}/simulation/{id}/percentage')


class RunCompleteWatcher(QThread):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    queued = Signal(int)
    started = Signal(object)
    completed = Signal(int)

    def get_simulations(self):
        pass
        # TODO this needs to be reimplemented over http

    def run(self):
        pass
        # TODO this needs to be reimplemented over http


def test_app():
    app = QApplication(sys.argv)
    label = QLabel("<font color=red size=40>Hello World!</font>")
    label.show()
    rcw = RunCompleteWatcher()
    sys.exit(app.exec_())


