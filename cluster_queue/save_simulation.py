import pickle
import numpy as np
import os
import model
from PIL import Image


def save_simulation(sim):
    """
    Save the images from a simulation. This is intended to be called before starting a simulation
    """

    simdir = model.run_directory(sim['id'])

    # Save rgb image
    # filename = f'{simdir}/rgb.png'
    # save_image(sim['rgb'], filename)

    # Save rgb image with contour
    filename = f'{simdir}/rgb_with_contour.png'
    save_image(sim['rgb_with_contour'], filename)

    # Save depth image
    filename = f'{simdir}/depth.png'
    save_image(sim['depth'], filename)


def save_image(img, filename):
    """
    Save the image given by an BGR numpy array as an image in a given location
    """
    rgb = np.uint8(img)
    rgb = rgb[:, :, ::-1]
    i = Image.fromarray(rgb)

    i.save(filename)
