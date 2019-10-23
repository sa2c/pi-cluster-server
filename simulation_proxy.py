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

def load_pickle_file(filename):
    """
    Utility function for loading simulations from the given file  `filename`
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_data_for_upload(data):
    """
    Save the image given by an BGR numpy array in `data` as an image in a given location
    """
    rgb = np.uint8(data)
    rgb = rgb[:, :, ::-1]
    i = Image.fromarray(rgb)

    img_bytes = io.BytesIO()
    i.save(img_bytes, format='PNG')

    return img_bytes.getvalue()

def sim_cache_filename(sim_id):
    """
    Returns the filename of the file in which simulation information will be cached locally
    """
    return 'sim-client-cache/{sim_id}.npy'.format(sim_id=sim_id)

def load_cached_sim(sim_id):
    """
    Load a cached simulation from simulation cache by sim_id
    """
    return load_pickle_file(sim_cache_filename(sim_id))

def redispatch_simulation(sim_id):
    """
    Function can be used to dispatch a simulation again from the client (as a new simulation). Note, this will create a brand new simulation dispatch.
    """
    sim = load_cached_sim(sim_id)
    return dispatch(sim)

def upload_images(sim_id, sim=None):
    """
    Upload images for sim_id. Sim can be provided if the function is called either without
    a cached simulation available or simply to avoid having to read from disk.
    """
    if sim is None:
        sim = load_cached_sim(sim_id)

    rgb_file = save_data_for_upload(sim['rgb_with_contour'])
    depth_file = save_data_for_upload(sim['depth'])

    url = f'{cluster_address}/upload/{sim["id"]}/rgb_with_contour.png'
    response = requests.post(url, data=rgb_file)

    if response.status_code != 200:
        logger(f'rgb image upload failed for simulation {sim["id"]}. retry with upload_images(sim_id)')


    url = f'{cluster_address}/upload/{sim["id"]}/depth.png'
    response = requests.post(url, data=depth_file)

    if response.status_code != 200:
        logger(f'depth image upload failed for simulation {sim["id"]}. retry with upload_images(sim_id)')


def dispatch(sim):
    """
    Posts data to server to create a new run of a simulation.
    Call redispatch_simulation to re-run this for a cached simulation.
    """

    # Save the full simulation locally in case we want to re-run anything
    # Note, this is done first in case recovery is necessary
    filename_tmp = sim_cache_filename('tmp')

    with open(filename, 'wb') as f:
        pickle.dump(sim, f)
    for key, val in sim.items():
        if type(val) == np.ndarray:
            sim[key] = val.tolist()

    # Upload simulation contour and information
    url_send = f'{cluster_address}/simulation/contour-info'
    send_keys = ['name', 'email', 'contour']
 
    send_sim = {key: sim[key] for key in send_keys}

    response = transfer_data.post_encoded(url_send, send_sim)

    if response.status_code != 200:
        # do something here to handle failure
        logger(f'simulation upload failed. Retry with redispatch_simulation(sim_id)')

    sim['id'] = response.json()['id']

    # moved temporary cached simulation file to final destination
    filename = sim_cache_filename(sim['id'])
    os.rename(filename_tmp, filename)

    # upload files, this is done by passing sim and sim_id so that it's easy to run
    upload_images(sim['id'])

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
