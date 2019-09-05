from subprocess import check_output
import numpy as np
import datetime
import calendar
import os
import json
import matplotlib.pyplot as plt

import settings
import model
import utils

from flask import Flask, request

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False


@app.route('/simulation', methods=['POST'])
def start_simulation():

    # extract simulation detail
    simulation = request.json

    sim_id = model.create_simulation(simulation)

    return {'id': str(sim_id)}


@app.route('/simulations', methods=['GET'])
def all_simulations():
    simulations = model.all_simulations()

    return simulations


@app.route('/simulation/<sim_id>/percentage', methods=['GET'])
def get_run_completion_percentage(sim_id):
    ''' Read the completion percentage of the run
    '''
    directory = model.run_directory(sim_id)

    utils.ensure_exists(directory)

    if not os.path.exists(directory):
        percentage = 0
    else:
        fname = f'{directory}/output'

        output = check_output(["grep", "MAIN:  Time", fname]).decode('utf-8')

        numer, denom = output.splitlines()[-1].split()[2].split("/")

        percentage = int(100 * float(numer) / float(denom))

    return {'percentage': percentage}


@app.route('/simulation/<id>', methods=['GET'])
def get_simulation(id):
    sim = model.get_simulation(id)

    return sim


@app.route('/simulations/max_drag/<nsims>', methods=['GET'])
def max_drag_simulation(nsims):

    ids = model.highest_drag_simulations_sorted(int(nsims))

    return {'ids': ids}


@app.route('/cluster/activity', methods=['GET'])
def get_activity():

    if settings.devel:
        cpu_usage = np.random.rand(12) * 100
    else:
        output = check_output(["bash", "cpuloadinfo.sh"]).decode('utf-8')

        cpu_usage = output.split('\n')[1:-1]
        cpu_usage = [
            float(cpu_usage_meas.split(' ')[1]) for cpu_usage_meas in cpu_usage
        ]

        cpu_usage = np.array(cpu_usage)

    return {'cpu_usage': cpu_usage.tolist()}


def run_filepath(index, filename):
    directory = run_directory(index)
    path = os.path.join(directory, filename)
    return path


def setup_cluster_inbox():
    utils.ensure_exists(settings.cluster_path + '/inbox')
    utils.ensure_exists(settings.cluster_path + '/signal_in')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3524, threaded=True)
