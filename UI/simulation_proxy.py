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


def dispatch(simulation):
    "Posts data to server to create a new run of a simulation"

    for key, val in simulation.items():
        if type(val) == np.ndarray:
            simulation[key] = val.tolist()

    response = requests.post(f'{cluster_address}/simulation', json=simulation)

    sim_id = response.json()['id']

    return sim_id


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
