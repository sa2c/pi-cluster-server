import pytest
import os, sys, shutil
import numpy as np
import json
import pickle

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import settings
from model import engine

settings.nnodes = 4
settings.nslots = 4
settings.IPs = [ "127.0.0.1" for i in range(settings.nnodes) ]
settings.cfdcommand = "ls" #Instead of actually running cfd

from server import app

@pytest.fixture
def client():
    global app
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    client = app.test_client()

    return client


###############
#### tests ####
###############

def assert_sim_equal(json_one, json_two):
    for key, value in json_two.items():
        assert json_one[key] == json_two[key]

def test_create_simulation(client):
    "create and check simulation"

    data_arrays = np.array([[1, 2, 3], [4, 5, 6]]).tolist()
    #data_arrays = json.dumps(data_arrays.tolist())

    json_data = {
        'name': 'Mr Funny',
        'email': 'funny@funnyland.com',
        'rgb': data_arrays,
        'rgb_with_contour': data_arrays,
        'depth': data_arrays,
        'background': data_arrays,
        'contour': data_arrays,
    }

    response = client.post('/simulation', json=json_data, follow_redirects=True)
    sim_id = response.json['id']

    assert type(sim_id) == str

    # get all simulations
    response = client.get('/simulations')
    json = response.json

    assert_sim_equal(json[sim_id], json_data)


    # fetch a specific simulation
    response = client.get(f'/simulation/{sim_id}')
    json = response.json

    assert_sim_equal(json, json_data)

def test_percenteage(client):
    sim_id = '1566995659'

    # fetch simulation completion percentage
    response = client.get(f'/simulation/{sim_id}/percentage')
    json = response.json

    assert json['percentage'] == 40

def test_activity(client):
    sim_id = '1566995659'

    # fetch simulation completion percentage
    response = client.get(f'/cluster/activity')
    json = response.json

    assert len(json['cpu_usage']) == 12

def test_dispatch_real_simulation(client):
    filename = 'simulation_sent_over_http.pickle'

    with open(filename, 'rb') as handle:
        simulation = pickle.load(handle)

    response = client.post('/simulation', json=simulation, follow_redirects=True)
    sim_id = response.json['id']
