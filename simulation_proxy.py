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
from PIL import Image

from settings import cluster_address

local_path = os.environ['PWD']

def logger(msg):
    print(msg)

def load_cached_sim(filename):
    """
    Utility function useful for loading simulations from disk for testing
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_data_as_image(data, filename):
    """
    Save the image given by an BGR numpy array as an image in a given location
    """
    rgb = np.uint8(data)
    rgb = rgb[:, :, ::-1]
    i = Image.fromarray(rgb)

    i.save(filename)

def save_data_for_upload(data, filename):
    filename = '/tmp/{filename}'.format(filename=filename)
    save_data_as_image(data, filename)
    return filename

def dispatch(sim):
    "Posts data to server to create a new run of a simulation"

    for key, val in sim.items():
        if type(val) == np.ndarray:
            sim[key] = val.tolist()

    url_early = f'{cluster_address}/simulation/contour-info'
    early_keys = ['name', 'email', 'contour']
 
    early_sim = {key: sim[key] for key in early_keys}

    response = transfer_data.post_encoded(url_early, early_sim)

    if response.status_code != 200:
        # do something here to handle failure
        logger(f'simulation upload failed')

    sim['id'] = response.json()['id']

    # upload files
    rgb_filename = save_data_for_upload(sim['rgb_with_contour'],'rgb_with_contour.png')
    depth_filename = save_data_for_upload(sim['depth'],'depth.png')

    with open(rgb_filename, 'rb') as f:
        url = f'{cluster_address}/upload/{sim["id"]}/rgb_with_contour.png'
        response = requests.post(url, data=f)

        if response.status_code != 200:
            logger(f'rgb_image upload failed for simulation {sim["id"]}')


    with open(depth_filename, 'rb') as f:
        url = f'{cluster_address}/upload/{sim["id"]}/depth.png'
        response = requests.post(url, data=f)

        if response.status_code != 200:
            logger(f'rgb_image upload failed for simulation {sim["id"]}')

    # Finally, we save the full simulation locally in case we want to re-run anything
    filename = 'sim-client-cache/{sim_id}.npy'.format(sim_id=sim['id'])

    with open(filename, 'wb') as f:
        pickle.dump(sim, f)

    return sim['id']


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
