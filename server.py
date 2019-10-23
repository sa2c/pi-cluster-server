#!/usr/bin/env python3.7
import numpy as np
import time
import datetime
import calendar
import os
import json
import matplotlib.pyplot as plt
import subprocess

import settings
import model
import utils

from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS

from werkzeug.serving import run_simple
from werkzeug.datastructures import FileStorage

from flask_webpack import Webpack
webpack = Webpack()

import transfer_data

def create_app():
    app = Flask(__name__)

    params = {
        'WTF_CSRF_ENABLED': False,
        'DEBUG': True,
        'WEBPACK_MANIFEST_PATH': 'webpack.manifest.json'
    }

    app.config['WTF_CSRF_ENABLED'] = False

    app.config.update(params)

    webpack.init_app(app)

    return app


app = create_app()

# Enable cross-site scripting
CORS(app)


# Static routes for simulation data
@app.route('/simulations/<path:filename>')
def custom_static(filename):
    return send_from_directory('simulations', filename)


# Root route (dashboard)
@app.route('/', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")


# HTML routes
@app.route('/results', methods=['GET'])
def results_html():
    return render_template("results.html")


@app.route('/activity', methods=['GET'])
def activity_html():
    return render_template("activity.html")


# Service routes


@app.route('/simulation/contour-info', methods=['POST'])
def start_simulation():

    # extract simulation detail
    simulation = transfer_data.post_decode(request)

    # change lists to np arrays in simulation
    for key, value in simulation.items():
        if type(value) == list:
            simulation[key] = np.array(value)

    sim_id = model.create_simulation(simulation)

    return {'id': str(sim_id)}

@app.route('/upload/<sim_id>/<filename>', methods=['POST'])
def simulation_handle_upload(sim_id, filename):
    filepath = model.sim_filepath(sim_id, filename)

    FileStorage(request.stream).save(filepath)

    return 'OK', 200

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
        fname = '{directory}/output'.format(directory=directory)

        output = check_output(["grep", "MAIN:  Time", fname]).decode('utf-8')

        numer, denom = output.splitlines()[-1].split()[2].split("/")

        percentage = int(100 * float(numer) / float(denom))

    return {'percentage': percentage}


@app.route('/simulation/<id>', methods=['GET'])
def get_simulation(id):
    sim = model.get_simulation(id)
    return sim


@app.route('/simulations/max_drag/<nsims>', methods=['GET'])
def max_drag_simulations(nsims):

    simulations = model.highest_drag_simulations_sorted(int(nsims))

    return json.dumps(simulations)


@app.route('/simulations/recent/<nsims>', methods=['GET'])
def most_recent_simulations(nsims):

    simulations = model.recent_simulations(int(nsims))

    return json.dumps(simulations)


def sims_filtered_keys(ids, keys):
    sims = [model.get_simulation(sid) for sid in ids]

    filtered = [{key: val
                 for key, val in sim.items() if key in keys} for sim in sims]

    return filtered

def string_to_rounded_int(str):
    return int(round(float(str)))

def read_usage():

    num_retries = 5

    # Because the file transfer might change files as they're being read, this could fail
    # Retry until success or num_retries

    for retries in range(num_retries):
        try:
            output_lines = subprocess.check_output('cat ~/cluster-load/info/* 2>/dev/null', shell=True).decode('utf8').split('\n')

            num_tries = retries + 1

            if num_tries > 1:
                print('warning: cpu usage reading attempt success at try {x}'.format(x=num_tries))
            break

        except subprocess.CalledProcessError as e:
            if(retries == retries - 1):
                raise(e)
            else:
                continue

        
    line_parts = [line.split() for line in output_lines if line[:7]=='10.0.0.']

    cpu_usage = {
            line[0] : string_to_rounded_int(line[1]) for line in line_parts
            }

    temp = {
            line[0] : int(float(line[2])*100/settings.pi_max_temp) for line in line_parts
            }


    return cpu_usage, temp

@app.route('/cluster/activity', methods=['GET'])
def get_activity():

    # Added safety layer to ensure that cpuinfo.txt isn't written to whilst being read
    # Note that this could still fail if activity called again before the request completes


    filter_keys = ['id', 'name', 'avatar', 'cores', 'images-available']

    pending = sims_filtered_keys(model.queued_simulations(), filter_keys)
    running = sims_filtered_keys(model.running_simulations(), filter_keys)

    running  = [ model.add_hostname_info(s) for s in running ]

    cpu_usage,temp = read_usage()

    response = {
        'time': time.time(),
        'cpu_usage': cpu_usage,
        'temp_percent': temp,
        'pending': pending,
        'running': running
    }

    return response


def run_filepath(index, filename):
    directory = run_directory(index)
    path = os.path.join(directory, filename)
    return path


def setup_cluster_inbox():
    utils.ensure_exists(settings.cluster_path + '/inbox')
    utils.ensure_exists(settings.cluster_path + '/signal_in')


if __name__ == '__main__':
    run_simple(hostname='0.0.0.0',
               port=settings.port,
               application=app,
               use_reloader=True,
               use_debugger=True,
               threaded=True)
