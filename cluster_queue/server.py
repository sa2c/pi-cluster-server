from subprocess import check_output
import numpy as np
import datetime
import calendar
import os
import pickle
import json
from computedrag import compute_drag_for_simulation
import matplotlib.pyplot as plt

import settings
import model

from flask import Flask, request

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False

@app.route('/simulation', methods=['POST'])
def start_simulation():

    # extract simulation detail
    simulation = request.json

    sim_id = model.create_simulation(simulation)

    return { 'id' : str(sim_id) }

@app.route('/simulations', methods=['GET'])
def all_simulations():
    simulations = model.all_simulations()

    return simulations

@app.route('/simulation/<id>/percentage', methods=['GET'])
def get_run_completion_percentage(id):
    ''' Read the completion percentage of the run
    '''
    directory = '{}/simulations/run{}'.format(settings.cluster_path, id)

    ensure_exists(directory)

    if not os.path.exists(directory):
        percentage = 0
    else:
        fname = f'/home/mark/code/picluster/cluster_queue/simulations/run{id}/output'

        output = check_output(["grep", "MAIN:  Time", fname]).decode('utf-8')

        numer, denom = output.splitlines()[-1].split()[2].split("/")


        percentage = int(100 * float(numer) / float(denom))

    return {'percentage' : percentage }

@app.route('/simulation/<id>', methods=['GET'])
def get_simulation(id):
    sim = model.get_simulation(id)

    return sim

@app.route('/simulations/max_drag/<nsim>', methods=['GET'])
def best_simulations(nsims):
    drag = np.array(drags)
    nsims = min(10, drag.shape[0])
    drag_sorted_indices = np.argsort(drag[:, 1])
    best_indices = drag[drag_sorted_indices[0:nsims], 0]

    simulations = [ load_simulation(int(i)) for index in best_indices ]

    return simulations

@app.route('/cluster/activity', methods=['GET'])
def get_activity():

    if settings.devel:
        cpu_usage = np.random.rand(12)*100
    else:
        output = check_output(["bash", "cpuloadinfo.sh"]).decode('utf-8')

        cpu_usage = output.split('\n')[1:-1]
        cpu_usage = [
            float(cpu_usage_meas.split(' ')[1]) for cpu_usage_meas in cpu_usage
        ]

        cpu_usage = np.array(cpu_usage)

    return {'cpu_usage' : cpu_usage.tolist()}

def ensure_exists(directory):
    "Creates a directory unless it exists"

    while not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            print(f'directory creation failed: {directory}')

def run_directory(index):
    directory = 'simulations/run{index}'.format(index=index)

    ensure_exists(directory)

    return directory

def run_filepath(index, filename):
    directory = run_directory(index)
    path = os.path.join(directory, filename)
    return path

def write_outline(filename, outline):
    "Takes an outline as an array and saves it to file outline file"
    outline = np.array(outline)
    flipped_outline = np.copy(outline.reshape((-1, 2)))
    flipped_outline[:, 1:] = 480 - flipped_outline[:, 1:]
    np.savetxt(filename, flipped_outline, fmt='%i %i')

def setup_cluster_inbox():
    ensure_exists(settings.cluster_path + '/inbox')
    ensure_exists(settings.cluster_path + '/signal_in')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3524, threaded=True)
