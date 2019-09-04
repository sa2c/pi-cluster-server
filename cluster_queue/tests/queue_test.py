import pytest
import os, sys, shutil
import numpy as np
import json
import pickle

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import settings
import model
import cluster_queue as queue

settings.nnodes = 4
settings.nslots = 4
settings.IPs = [ "127.0.0.1" for i in range(settings.nnodes) ]
#settings.cfdcommand = "ls" #Instead of actually running cfd

from server import app

###############
#### tests ####
###############

def test_run_simulation():
    "create and check simulation"

    # read simulation
    filename = 'sent_over_http_simulation.pickle'

    with open(filename, 'rb') as handle:
        simulation = pickle.load(handle)

    sim_id = model.create_simulation(simulation)

    process = queue.run_simulation(sim_id)
