import status_codes
import numpy as np
import utils
import settings
import os
import subprocess
import pickle
from PIL import Image
import glob
from functools import lru_cache

STATUS_CREATED = 'status.created'
STATUS_ADDITIONAL_INFO = 'status.info'
STATUS_STARTED = 'status.started'
STATUS_FINISHED = 'status.finished'


def choose_avatar():
    return int(random.random() * 25) + 1


######################################
## Paths
######################################


def clean_sim_id(sim_id):
    return int(sim_id)


def sim_filepath(simulation_id, filename):
    return run_directory(simulation_id) + '/' + filename


def sim_datafile(simulation_id):
    return sim_filepath(simulation_id, 'data.pickle')

def run_directory(index):
    directory = '{sim_dir}/{index}'.format(sim_dir=simulation_store_directory(), index=index)

    utils.ensure_exists(directory)

    return directory


def simulation_store_directory():
    directory = '{root_dir}/simulations'.format(root_dir=settings.root_dir)

    utils.ensure_exists(directory)

    return directory


def drag_file(sim_id):
    return sim_filepath(sim_id, 'drag.txt')


def touch_file(sim_id, filename):
    open(sim_filepath(sim_id, filename), 'a').close()

def sim_check_file(sim_id, filename):
    return os.path.isfile(sim_filepath(sim_id, filename))

def check_status(sim_id, status):
    return sim_check_file(sim_id, status)

def set_started(sim_id):
    touch_file(sim_id, STATUS_STARTED)

def set_finished(sim_id):
    touch_file(sim_id, STATUS_FINISHED)

######################################
## Pickle and save/load utils
######################################


def pickle_save(filename, data):
    """
    Pickles data to a given filename. Note, it writes using a temporary file to
    avoid that file is read before finished writing.
    """

    filename_tmp = filename + 'tmp'

    with open(filename_tmp, 'wb') as f:
        pickle.dump(data, f)

    os.rename(filename_tmp, filename)

    return data

@lru_cache(maxsize=10)
def pickle_load(filename):
    with open(filename, 'rb') as f:
        sim = pickle.load(f)
    return sim


def save_data_as_image(data, filename):
    """
    Save the image given by an BGR numpy array as an image in a given location
    """
    rgb = np.uint8(data)
    rgb = rgb[:, :, ::-1]
    i = Image.fromarray(rgb)

    i.save(filename)


######################################
## Utils
######################################


def generate_sim_id():
    current_ids = simulation_id_list()

    if len(current_ids) == 0:
        next_id = 1
    else:
        next_id = int(np.max(current_ids) + 1)

    return next_id


def simulation_id_list():
    sim_store = simulation_store_directory()
    return [
        clean_sim_id(os.path.basename(i))
        for i in glob.glob('{sim_store}/[0-9]*'.format(sim_store=sim_store))
    ]

def is_sim_running(sim_id):
    sim_id = clean_sim_id(sim_id)

    return check_status(
        sim_id, STATUS_STARTED) and not check_status(sim_id, STATUS_FINISHED)

def is_sim_queued(sim_id):
    sim_id = clean_sim_id(sim_id)

    return check_status(
        sim_id, STATUS_CREATED) and not check_status(sim_id, STATUS_STARTED)


def get_drag(sim_id):
    filename = drag_file(sim_id)

    if os.path.isfile(filename):
        with open(filename) as file:
            return float(file.read())
    else:
        return None


def all_drags():
    ids = np.array(simulation_id_list())
    drags = np.array([get_drag(i) for i in ids])

    notNone = [i for i in range(len(drags)) if drags[i] is not None]

    ids = ids[notNone].astype(np.int32)
    drags = drags[notNone].astype(np.int32)

    return (drags, ids)


def sims_by_id(ids):
    return [get_simulation(sim) for i in simulation_id_list()]


def set_drag(sim_id, drag):
    filename = drag_file(sim_id)

    with open(filename, 'w') as file:
        file.write(str(drag))


######################################
## Public API
######################################


def create_simulation(sim):
    sim_id = generate_sim_id()
    sim['id'] = sim_id

    filename = sim_datafile(sim['id'])

    pickle_save(filename, sim)

    touch_file(sim_id, STATUS_CREATED)

    return sim_id

def valid_simulations(id_list):
    # get_simulation can return None if a non-simulation directory exists in
    # simulations or if the pickle file is half-written

    return [s for s in [get_simulation(i) for i in id_list] if s is not None]


def all_simulations():
    return valid_simulations(simulation_id_list())

def get_ip_info(sim_id):
    hostfilename = sim_filepath(sim_id, 'hostfile')
    with open(hostfilename) as f:
        ips = [ line.split(" ")[0] for line in f.readlines() ]

    return ips

def add_hostname_info(sim):
    sim['cores'] = get_ip_info(sim['id'])
    return sim

def queued_simulations():
    return [ s for s in simulation_id_list() if is_sim_queued(s) ]

def running_simulations():
    return [ s for s in simulation_id_list() if is_sim_running(s) ]

def get_simulation(sim_id):
    """
    Returns simulation data for a simulation if the data file exists and the created flag exists. Otherwise returns None.
    """
    sim_id = clean_sim_id(sim_id)

    datafile = sim_datafile(sim_id)

    if check_status(sim_id, STATUS_CREATED) and os.path.isfile(datafile):
        simulation = pickle_load(datafile)
        simulation['drag'] = get_drag(sim_id)

        # set the images available key for simulation
        simulation['images-available'] = sim_check_file(sim_id, 'rgb_with_contour.png') and sim_check_file(sim_id, 'depth.png')

        return simulation
    else:
        return None


def write_outline(sim_id, outline):
    "Takes an outline as an array and saves it to file outline file"
    filename = outline_coords_file(sim_id)
    outline = np.array(outline)
    flipped_outline = np.copy(outline.reshape((-1, 2)))
    flipped_outline[:, 1:] = 480 - flipped_outline[:, 1:]
    np.savetxt(filename, flipped_outline, fmt='%i %i')


def run_simulation(sim_id, hostfilename):
    """
    Note: Should only really be called by queue manager, otherwise who knows where the process would be
    """

    simulation = get_simulation(sim_id)

    write_outline(sim_id, simulation['contour'])

    command = settings.cfdcommand.format(id=sim_id,
                                         ncores=settings.nodes_per_job *
                                         settings.cores_per_node,
                                         hostfile=hostfilename,
                                         output=sim_filepath(sim_id, 'output'))

    print('RUNNING SIMULATION: {command}'.format(command=command))
    set_started(sim_id)
    process = subprocess.Popen(command, shell=True)
    set_finished(sim_id)

    return process


def outline_coords_file(sim_id):
    return sim_filepath(sim_id, 'outline-coords.dat')


def highest_drag_simulations_sorted(num_sims=10):
    "fetches `num_sims` simulations and order them by value of drag"

    drags, sim_ids = all_drags()
    idxs = np.argsort(drags)[:num_sims]

    result_sim_ids = sim_ids[idxs]

    return valid_simulations(result_sim_ids)


def recent_simulations(num_sims=10):
    "fetches `num_sims` simulations with the highest ID"

    recent_sim_ids = sorted(simulation_id_list(), reverse=True)[:num_sims]

    return valid_simulations(recent_sim_ids)
