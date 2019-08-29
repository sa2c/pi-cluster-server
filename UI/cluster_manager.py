from PySide2.QtCore import *
import numpy as np
from fabric import Connection
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

# Check connection
print("Checking connection to the head node.")
c = Connection(cluster_address)
c.open()
c.close()


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
    with Connection(cluster_address) as cluster:
        with cluster.cd(cluster_path):
            output = cluster.run('''bash cpuloadinfo.sh''', hide=True).stdout
        cpu_usage = output.split('\n')[1:-1]
        cpu_usage = [
            float(cpu_usage_meas.split(' ')[1]) for cpu_usage_meas in cpu_usage
        ]
        cpu_usage = np.array(cpu_usage)
        return cpu_usage

def get_run_completion_percentage(index):
    response = requests.post(f'{cluster_address}/simulation/{id}/percentage')
    import pdb; pdb.set_trace()


def create_incoming_signal( index, signal_type, slot):
    ''' create an incoming signal, only useful for testing '''
    with Connection(cluster_address) as cluster:
        filename = 'signal_out/run{}_{}_{}'.format(index, signal_type, slot)
        path = cluster_path+'/'+filename
        cluster.sftp().open(path, 'a').close()


def remove_incoming_signal(signal):
    ''' remove a signal, only useful for testing '''
    global existing_signals
    path = cluster_path+'/signal_out/'+signal
    if os.path.exists(path):
        os.remove(path)
    existing_signals = existing_signals - set(signal)
    

def get_new_signals():
    global existing_signals
    signals = get_signals()
    return signals - existing_signals


def add_new_signal(signal):
    global existing_signals
    existing_signals.add(signal)


def get_signal_info(signal):
    run, signal_type, slot = signal.split('_')
    slot = int(slot)
    index = run.replace("run", '')
    index = int(index)
    return index, signal_type, slot


def get_slot(index):
    for signal in get_signals():
        signal_index, signal_type, slot = get_signal_info(signal)
        if signal_index == index:
            return slot

def download_results(index):
    with Connection(cluster_address) as cluster:
        localfolder = run_directory(index)
        remotefolder = 'simulations/run{}'.format(index)
        remotepath = cluster_path+'/'+remotefolder
        try:
            dirlist = cluster.sftp().listdir(remotepath)
        except:
            print("Could not download",remotepath)
            return

        for filename in dirlist:
            localfile = os.path.join(localfolder,filename)
            remotefile = remotepath+'/'+filename
            if not os.path.isfile(localfile):
                cluster.sftp().get( remotefile, localfile )


def queue_running():
    cluster = Connection(cluster_address)
    setup_cluster_inbox()
    remote_name = '{}/signal_in/ping'.format(cluster_path)
    cluster.sftp().file(remote_name, 'a').close()

    remote_name = '{}/signal_out/pong'.format(cluster_path)
    for i in range(5):
        try:
            cluster.sftp().remove(remote_name)
            return True
        except IOError:
            time.sleep(1)

    return False


def restart_slot(slot):
    cluster = Connection(cluster_address)
    path = '{}/signal_in/restart{}'.format(cluster_path,slot)
    cluster.sftp().file(path, 'a').close()


class RunCompleteWatcher(QThread):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    queued = Signal(int)
    started = Signal(object)
    completed = Signal(int)

    def get_simulations(self):
        # TODO this needs to be reimplemented over http

    def run(self):
        self.get_simulations()
        while True:
            for signal in get_new_signals():
                add_new_signal(signal)
                index, signal_type, slot = get_signal_info(signal)

                print("{} signal for run {} in slot {}!".format(
                    signal_type, index, slot))

                if signal_type == "start":
                    download_results(index)
                    self.started.emit((index, slot))
                elif signal_type == "end":
                    download_results(index)
                    self.completed.emit(index)
                elif signal_type == "queue":
                    download_results(index)
                    self.queued.emit(index)

            time.sleep(2)



def test_app():
    app = QApplication(sys.argv)
    label = QLabel("<font color=red size=40>Hello World!</font>")
    label.show()
    rcw = RunCompleteWatcher()
    sys.exit(app.exec_())


