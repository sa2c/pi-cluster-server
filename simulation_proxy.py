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
import transfer_data
import pickle

from settings import cluster_address

local_path = os.environ['PWD']


def dispatch(simulation):
    "Posts data to server to create a new run of a simulation"

    for key, val in simulation.items():
        if type(val) == np.ndarray:
            simulation[key] = val.tolist()

    url_early = f'{cluster_address}/simulation/contour-info'
    url_rest = f'{cluster_address}/simulation/additional-info'
    early_keys = ['name', 'email', 'contour']

    # First we send only the outline data (so that simulation can start)
    print("Sending Contour Info")
    early_simulation = {key: simulation[key] for key in early_keys}

    response = transfer_data.post_encoded(url_early, early_simulation)

    simulation['id'] = response.json()['id']

    # Next we send the rest of the data
    print("Sending Additional Info")
    rest_simulation = {key: simulation[key] for key in simulation.keys()
                       if key not in early_keys}

    response = transfer_data.post_encoded(url_rest, rest_simulation)

    # Finally, we save the simulation locally in case anything goes wrong
    filename = 'sim-client-cache/{sim_id}.npy'.format(sim_id=simulation['id'])

    with open(filename, 'wb') as f:
        pickle.dump(simulation, f)

    return simulation['id']


def fetch_all():
    "fetches a list of all simulations and their details from the server"
    response = requests.get(f'{cluster_address}/simulations')
    simulations = response.json()

    return simulations


def fetch_activity():
    response = requests.get(f'{cluster_address}/cluster/activity')
    cpu_usage = response.json()['cpu_usage']

    return cpu_usage


def fetch_max_drag(number):
    response = requests.get(f'{cluster_address}/simulations/max_drag/{number}')

    ids = response.json()['ids']

    return ids


def get_run_completion_percentage(index):
    response = requests.post(f'{cluster_address}/simulation/{id}/percentage')


def load_simulation(index):
    response = requests.get(f'{cluster_address}/simulation/{index}')

    return response.json()


def load_simulation_name(index):
    pass
