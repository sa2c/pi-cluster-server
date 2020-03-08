import glob, json, pathlib, os
from simulation_proxy import convert_image_to_bytes
import pickle
import cv2


def cache_dir():
    '''
    Returns the directory in which snapshots are stored
    '''
    snapshot_dir = pathlib.Path(__file__).parent.absolute()
    directory = f'{snapshot_dir}/snapshot-cache'

    attempt_mkdir(directory)

    return directory


def ids():
    '''
    Returns a list of all available snapshot identifiers
    '''
    snapshot_dirs = glob.glob(f'{cache_dir()}/*')

    return [int(snapshot.split('/')[-1]) for snapshot in snapshot_dirs]


def get_contour(id):
    '''
    Gets a normalised contour from cache
    '''

    contour = read_contour(id)

    return normalise_points(contour, width=640, height=480)


def normalise_points(points, width, height):
    '''
    Transform units of width and height to be between 0 and 1
    '''
    return [[point[0] / width, point[1] / height] for point in points]


def read_contour(id):
    '''
    Reads a contour from a .json file
    '''
    with open(f'{cache_dir()}/{id}/contour.json', 'r') as f:
        contents = f.readlines()

    contents = ''.join(contents)

    try:
        contour = json.loads(contents)
    except json.JSONDecodeError:
        contour = []

    return contour


def attempt_mkdir(directory):
    '''
    Attempts to make a directory, to ensure that it exists
    '''
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass


def get_filepath(identifier, name):
    '''
    Returns the full path to persistant storage file with `name` for given identifier.
    '''

    directory = f'{cache_dir()}/{identifier}'
    attempt_mkdir(directory)

    filepath = f'{directory}/{name}'

    return filepath


def write_image(filepath, image):
    '''
    Writes a PIL image object to filepath as a PNG file
    '''

    with open(filepath, 'wb') as f:
        f.write(convert_image_to_bytes(image))


def write_contour(contour, contour_filename):
    '''
    Writes the contour to a json file
    '''
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


def update_from_cache(identifier, snapshot_data):
    '''
    Updates the `snapshot_data` dictionary with information from the snapshot cache.
    Existing information is overwritten with information from the cache.
    '''

    snapshot_cache = read_sim_cache(identifier)

    # update the snapshots with the simulation information
    snapshot_data.update(snapshot_cache)


def draw_contour_on_image(image, contour):
    '''
    Draw `contour` onto `image`
    '''
    image_with_contour = image.copy()

    cv2.drawContours(image_with_contour, [contour], -1, (0, 0, 255), 2)

    return image_with_contour


def delete_snapshot(id):
    '''
    Delete cache for snapshot with a given `id`
    '''

    cache_path = os.path.join(cache_dir(), str(id))

    os.system(f'rm -rf {cache_path}')
