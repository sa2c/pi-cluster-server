import json, time
import numpy as np
from kinectlib import kinectlib as kinect
from snapshots import snapshots
import os
import yaml

default_settings = {
    # all times are in tenths of a second
    'interval': 0,
    'interval-cleanup': 5,
    'update-interval': 30 * 10,
    'max-count': 0
}

settings = default_settings.copy()

## Handle setting background (used from another function)

__background = None


def get_background():
    global __background

    return __background


def set_background(background):
    global __background
    __background = background


def fetch_settings_from_file():
    '''
    Read settings from settings.yaml, or return an empty dict if file does not exist
    '''
    settings_file = r'snapshots/settings.yaml'

    if os.path.isfile(settings_file):
        with open(settings_file) as settings_file:
            return yaml.load(settings_file, Loader=yaml.FullLoader)
    else:
        return {}


def update_settings():
    '''
    Update the global settings from contents of settings file
    '''
    global settings

    new_settings = default_settings.copy()

    new_settings.update(fetch_settings_from_file())

    if new_settings != settings:
        settings = new_settings
        print('Settings updated.')
        print(settings)


def compute_contour(image, depth, depthimage, background):
    '''
    Creates a contour from image and depth.
    '''
    scale = [1.0, 1.0]
    offset = [0.0, 0.0]

    rgb_frame = np.copy(kinect.device.get_video())

    clean_depth = kinect.remove_background(depth, background)
    contour_orig = kinect.normalised_depth_to_contour(clean_depth)

    # I'm not sure why the code does the scaling twice - but have repeated here
    transformed_contour = kinect.transform_contour(contour_orig, scale, offset)
    contour = kinect.scale_and_translate_contour(transformed_contour, scale,
                                                 offset)

    return contour


def snapshots_to_delete(num_to_keep=0):
    all_ids = snapshots.ids()
    all_ids.sort(reverse=True)

    return all_ids[num_to_keep:]


def cleanup_snapshots(num_to_keep):
    to_delete = snapshots_to_delete(num_to_keep)

    for snap in to_delete:
        snapshots.delete_snapshot(snap)


def write_video_maybe(image, depthimage, depth):
    '''
    This is called for every frame, giving the opportunity to write the video to disk.
    Depth is already a time-averaged depth at this point.
    '''

    background = get_background()

    # unix epoch computed in tenths of a second
    epoch = int(time.time() * 10)

    # set variables from settings
    interval = settings['interval']
    update_interval = settings['update-interval']
    interval_cleanup = settings['interval-cleanup']
    max_count = settings['max-count']

    # update settings periodically
    if update_interval > 0 and epoch % update_interval:
        update_settings()

    # do periodic cleanup and snapshot recording

    if max_count > 0:
        if interval > 0 and epoch % interval == 0 and background is not None:
            write_video(image, depthimage, depth, background, epoch)

        if interval_cleanup > 0 and epoch % interval_cleanup == 0:
            cleanup_snapshots(max_count)


def write_video(image, depthimage, depth, background, identifier):
    '''
    Writes periodic data to disk, at a given location
    Note, this function reads background from globals
    '''

    image_filename = snapshots.get_filepath(identifier, 'image.png')
    depthimage_filename = snapshots.get_filepath(identifier, 'depth.png')
    contour_filename = snapshots.get_filepath(identifier, 'contour.json')

    snapshots.write_image(image_filename, image)
    snapshots.write_image(depthimage_filename, depthimage)

    # Write contour to disk as json
    contour = compute_contour(image, depth, depthimage, background)

    # remove_additional_dimension
    contour = contour[:, 0, :]

    # cache simulation data in format required for upload/dispatch
    sim = {
        'rgb': image,
        'depth': depthimage,
        'background': background,
        'rgb_with_contour': snapshots.draw_contour_on_image(image, contour),
        'contour-orig': contour
    }

    snapshots.write_contour(contour, contour_filename)

    snapshots.write_sim_cache(identifier, sim)
