import glob, json, pathlib, os
from simulation_proxy import convert_image_to_bytes
import pickle

def dir():
    snapshot_dir = pathlib.Path(__file__).parent.absolute()
    directory = f'{snapshot_dir}/snapshot-cache'

    attempt_mkdir(directory)

    return directory

def ids():
    snapshot_dirs = glob.glob(f'{dir()}/*')

    return [ int(snapshot.split('/')[-1]) for snapshot in snapshot_dirs ]

def normalise_points(points, width, height):
    return [[ point[0] / width, point[1] / height ]  for point in points]

def get_contour(id):
    contour = read_contour(id)
    return normalise_points(contour, width=640, height=480)


def read_contour(id):
    with open(f'{dir()}/{id}/contour.json', 'r') as f:
        contents = f.readlines()

    contents = ''.join(contents)

    try:
        contour = json.loads(contents)
    except json.JSONDecodeError:
        contour = []

    return contour

def attempt_mkdir(directory):
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

def get_filepath(identifier, name):
    '''
    Returns the pathname of a file to store for given identifier.
    '''

    directory = f'{dir()}/{identifier}'
    attempt_mkdir(directory)

    filepath = f'{directory}/{name}'

    return filepath

def write_image(filepath, image):

    with open(filepath, 'wb') as f:
        f.write(convert_image_to_bytes(image))

def cache_filepath(image_name):
    pass

def write_contour(contour, contour_filename):
    with open(contour_filename, 'w') as outfile:
        json.dump(contour.tolist(), outfile)

def write_sim_cache(identifier, sim):
    '''
    Write the simulation data to a pickle file for a given snapshot identifier.
    '''
    with open(get_filepath(identifier, 'sim-cache.pickle'), 'wb') as f:
        pickle.dump(sim, f)

def read_sim_cache(identifier):
    '''
    Reads the simulation data from a pickle file for a given snapshot identifier.
    '''
    with open(get_filepath(identifier, 'sim-cache.pickle'), 'rb') as f:
        sim = pickle.load(f)

    return sim
