from PySide2.QtCore import *
import numpy as np
import os, io
import time
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


def queue_run(contour, index):
    with Connection(cluster_address) as cluster:
        # save contour to file and copy to the cluster inbox
        filename = run_filepath(index, "contour.dat")
        write_outline(filename, contour)

        setup_cluster_inbox()

        # copy the contour
        remote_name = '{}/inbox/run{}'.format(cluster_path, index)
        cluster.put(filename, remote=remote_name)

        # copy simulation details over to the cluster
        remote_folder = '{}/simulations/run{}'.format(cluster_path, index)
        cluster.sftp().mkdir(remote_folder)
        local_folder  = 'simulations/run{}'.format(index)
        for filename in os.listdir(local_folder):
            remote_file  = '{}/{}'.format(remote_folder, filename)
            local_file  = '{}/{}'.format(local_folder, filename)
            cluster.put(local_file, remote=remote_file)

        # copy a signal file across
        remote_name = '{}/signal_in/run{}'.format(cluster_path, index)
        cluster.sftp().file(remote_name, 'a').close()


def save_and_run_simulation(simulation):
    # determining the index should be on the server really
    now = datetime.datetime.utcnow()
    index = calendar.timegm(now.utctimetuple())

    simulation['index'] = index

    save_simulation(simulation)
    queue_run(simulation['contour'], simulation['index'])


    return index

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

def save_simulation(simulation):

    name = simulation['name']
    index = simulation['index']

    # save name
    with open(run_filepath(index, 'name.npy'), 'wb') as file:
        pickle.dump(name, file, protocol=pickle.HIGHEST_PROTOCOL)

    # save simulation
    with open(run_filepath(index, 'simulation.npy'), 'wb') as file:
        pickle.dump(simulation, file, protocol=pickle.HIGHEST_PROTOCOL)


def load_simulation(index):
    # save simulation
    with open(run_filepath(index, 'simulation.npy'), 'rb') as file:
        return pickle.load(file)


def fetch_activity():
    response = requests.get(f'{cluster_address}/cluster/activity')

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


