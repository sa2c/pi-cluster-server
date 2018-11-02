from PySide2.QtCore import *
import numpy as np
from fabric import Connection
import os

cluster_address = "pi@10.0.0.253"
cluster_path = "Documents/picluster"
local_path = os.environ['PWD']
nmeasurements = 20
cluster = Connection(cluster_address)


def all_available_indices_and_names():
    dir = 'outbox'
    simulations = []

    for file in os.listdir(dir):
        if 'run' in file:
            try:
                index = int(file.replace('run', ''))
                name = str(np.load(run_filepath(index, 'name.npy')))
                simulations.append([index, name])
            except:
                print(f'failed to load file: {file}')

    return simulations


def run_directory(index):
    directory = 'outbox/run{index}'.format(index=index)

    while not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print(f'directory creation failed: {directory}')

    return directory


def run_filepath(index, filename):
    directory = run_directory(index)
    path = os.path.join(directory, filename)
    return path


def get_cfd_output(index):
    ''' Get the current stdout of the ongoing run
        or the previous run.
    '''
    directory = '{}/outbox/run{}'.format(cluster_path, index)
    with cluster.cd(directory):
        return cluster.run('cat output', hide=True).stdout


def get_run_completion_percentage(index):
    ''' Read the completion percentage of the run
    '''
    output = get_cfd_output(index)

    found = False
    try:
        for line in output.split("\n"):
            if "MAIN:  Time:" in line:
                timestring = line.split(' ')[3]
            numbers = timestring.split('/')
            percentage = float(numbers[0]) / float(numbers[1])
        else:
            percentage = 0
    except:
        percentage = 0
    return percentage


def write_outline(filename, outline):
    flipped_outline = np.copy(outline.reshape((-1, 2)))
    flipped_outline[:, 1:] = 480 - flipped_outline[:, 1:]
    np.savetxt(filename, flipped_outline, fmt='%i %i')


def queue_run(contour, index):
    # save contour to file and copy to the cluster inbox
    filename = run_filepath(index, "contour.dat")
    write_outline(filename, contour)

    # copy the contour
    remote_name = '{}/inbox/run{}'.format(cluster_path, index)
    cluster.put(filename, remote=remote_name)

    # copy a signal file accross
    remote_name = '{}/signal/run{}'.format(cluster_path, index)
    cluster.put(filename, remote=remote_name)


class RunCompleteWatcher(QFileSystemWatcher):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    started = Signal(int, int)
    completed = Signal(int)

    def __init__(self, parent=None):
        self.existing_runs = set(os.listdir("{}/signal/".format(local_path)))

        path = "{}/signal/".format(local_path)
        super().__init__([path], parent)

        self.directoryChanged.connect(self.run_complete)

    def run_complete(self, path):
        runs = set(os.listdir(path))

        new_runs = runs - self.existing_runs

        for run in new_runs:
            run, signal, slot = run.split('_')
            index = run.replace("run", '')
            index = int(index)
            print("{} signal for run {}!".format(signal, index))
            self.existing_runs.add(run)
            if signal == "start":
                self.started.emit(index, slot)
            elif signal == "end":
                self.completed.emit(index)


def test_submit():
    contour = np.loadtxt("scf1540984574-outline-coords.dat")
    queue_run(contour, 2)
    while True:
        print(get_run_completion_percentage(2))
        time.sleep(1)


def test_app():
    app = QApplication(sys.argv)
    label = QLabel("<font color=red size=40>Hello World!</font>")
    label.show()
    rcw = RunCompleteWatcher()
    sys.exit(app.exec_())
