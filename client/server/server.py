import json, time
import numpy as np
from kinectlib import kinectlib as kinect
from server.settings import snapshots_dir

from simulation_proxy import convert_image_to_bytes
import os

## Handle setting background (used from another function)

__background = None

def get_background():
    global __background

    return __background

def set_background(background):
    global __background
    __background = background


# Write images to disk

def write_image_to_disk(filepath, image):

    with open(filepath, 'wb') as f:
        f.write(convert_image_to_bytes(image))

def write_json_to_disk(filename, json_data):
    pass

# Maybe write the video

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
    contour = kinect.scale_and_translate_contour(transformed_contour, scale, offset)

    return contour

def write_video_maybe(image, depthimage, depth):
    '''
    This is called for every frame, giving the opportunity to write the video to disk.
    Depth is already a time-averaged depth at this point.
    '''

    background = get_background()

    if background is not None:

        epoch = int(time.time())

        if epoch % 4 == 0:
            write_video(image, depthimage, depth, background, epoch)

def cache_filepath(name, epoch):
    '''
    Returns the directory to store a given epoch.
    '''

    directory = f'{snapshots_dir()}/{epoch}'
    filepath = f'{directory}/{name}'

    try:
        os.mkdir(directory)
    except:
        pass

    return filepath

def write_video(image, depthimage, depth, background, epoch):
    '''
    Writes periodic data to disk, at a given location
    Note, this function reads background from globals
    '''

    image_filename = cache_filepath('image.png', epoch)
    depthimage_filename = cache_filepath('depth.png', epoch)
    contour_filename = cache_filepath('contour.json', epoch)

    write_image_to_disk(image_filename, image)
    write_image_to_disk(depthimage_filename, depthimage)

    # Write contour to disk as json
    contour = compute_contour(image, depth, depthimage, background)

    # remove_additional_dimension
    contour = contour[:,0,:]

    with open(contour_filename, 'w') as outfile:
        json.dump(contour.tolist(), outfile)
