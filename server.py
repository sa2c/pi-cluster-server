#!/usr/bin/env python3.7
import numpy as np
import time
import datetime
import calendar
import os
import json
import matplotlib.pyplot as plt

import settings
import model
import utils

from flask import Flask, request, render_template, send_from_directory
from werkzeug.serving import run_simple

from flask_webpack import Webpack
webpack = Webpack()


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


@app.route('/cluster/activity', methods=['GET'])
def get_activity():

    # Added safety layer to ensure that cpuinfo.txt isn't written to whilst being read
    # Note that this could still fail if activity called again before the request completes
    with open("cpuinfo.txt", "r") as f:
        output = f.readlines()

    lines = [ l[:-1].split(' ') for l in output ]

    cpu_usage = {
           info[0] : float(info[1]) for info in lines
    }


    filter_keys = ['id', 'name', 'avatar', 'cores']

    pending = sims_filtered_keys(model.queued_simulations(), filter_keys)
    running = sims_filtered_keys(model.running_simulations(), filter_keys)

    running  = [ model.add_hostname_info(s) for s in running ]

    response = {
        'time': time.time(),
        'cpu_usage': cpu_usage,
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
               port=3524,
               application=app,
               use_reloader=True,
               use_debugger=True,
               threaded=True)
