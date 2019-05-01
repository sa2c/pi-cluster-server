
import cv2, sys, time, os
import numpy as np
from scipy import interpolate
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from kinectlib.calibration import affine_calibration as affc

from settings import dmin, dmax, min_distance
from settings import num_points, corner_cutting_steps
from settings import color_scale, flip_display_axis
from settings import mock_kinect

if not mock_kinect:
    # Use the actual kinect. Requires freenect to be installed
    from freenect import sync_get_depth, sync_get_video
    from freenect import DEPTH_MM

if mock_kinect:
    # Use recorded Kinect data to mock the device. Load the data
    # from kinect_data.npy and color_kinect_data.npy here.
    global mock_kinect_index, mock_depth, mock_color
    print('WARNING: MOCKING KINECT')
    mock_kinect_index = 0

    mock_depth = np.load("test_data/kinect_data.npy")
    mock_color = np.load("test_data/color_kinect_data.npy")


def get_depth():
    if mock_kinect:
        global mock_kinect_index, mock_depth, mock_color
        mock_kinect_index = mock_kinect_index + 1
        index = mock_kinect_index % len(mock_depth)
        depth = np.copy(mock_depth[index])
    else:
        (depth, _) = sync_get_depth(format=DEPTH_MM)
        depth = np.copy(depth)

    if flip_display_axis:
        depth = np.fliplr(depth)

    return depth


def get_video():
    global color_scale
    if mock_kinect:
        global mock_kinect_index, mock_depth, mock_color
        index = mock_kinect_index % len(mock_color)
        rgb = np.copy(mock_color[index])
    else:
        (rgb, _) = sync_get_video()
        rgb = np.copy(rgb)

    # scale colours by colour calibration
    rgb[:, :, 0] = rgb[:, :, 0] * color_scale[0]
    rgb[:, :, 1] = rgb[:, :, 1] * color_scale[1]
    rgb[:, :, 2] = rgb[:, :, 2] * color_scale[2]

    if flip_display_axis:
        rgb = np.fliplr(rgb)

    return invert_color_order(rgb)


# Mock data for testing
def get_mock_video():
    return np.load("test_data/color_image.npy")


def get_mock_depth():
    return np.load("test_data/depth_image.npy")


def get_mock_background_depth():
    return np.load("test_data/depth_background_image.npy")


def invert_color_order(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)


def set_color_scale(rgb):
    global color_scale
    color_scale = rgb


def get_color_scale():
    global color_scale
    return color_scale


def threshold(d):
    t = d * (d >= 1) + dmax * (d < 1)
    t = (t - dmin) * (t > dmin)
    t = t * (d < dmax) + (dmax - dmin) * (d >= dmax)
    t = (t.astype(np.float32) * 255 / (dmax - dmin))
    return t


def measure_depth(n=1):
    depth = get_depth()
    depth = threshold(depth)
    depth = depth.astype(np.float32) / n
    for m in range(1, n):
        d = get_depth()
        d = threshold(d)
        d = d.astype(np.float32) / n
        depth += d
    return depth


def remove_background(im, bg):
    diff = im - bg
    return im * (diff < -3) + 254 * (diff >= -3)


def depth_to_depthimage(depth):
    cmap = plt.get_cmap('brg')
    depth = (depth / np.max(depth))
    depthimage_rgba = cmap(depth) * 127
    depthimage = np.delete(depthimage_rgba, 3, 2)

    return depthimage.astype(np.uint8)


def normalised_depth_to_contour(depth):
    cutimage = np.dstack((depth, depth, depth)).astype(np.uint8)

    #Find contour
    gray = cv2.cvtColor(cutimage, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, min_distance, 255,
                                   cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contour = max(contours, key=cv2.contourArea)
    return np.array(contour).astype(int)


def cut_corners(outline, n):
    for i in range(n):
        outline = np.append(outline, [outline[0, ]], axis=0)
        R = outline[1:]
        L = outline[:outline.shape[0] - 1]
        outline = 0.5 * L + 0.5 * R
    return outline


def transform_contour(contour, scale, offset):
    outline = contour[:, 0, :]
    outline = cut_corners(outline, corner_cutting_steps)
    tck, u = interpolate.splprep(outline.transpose(), s=10)
    du = 1 / (num_points)
    unew = np.arange(0, 1.0, du)
    outline = interpolate.splev(unew, tck)
    outline = np.array(outline)

    transformed_outline = np.copy(outline)

    # apply affine transform from calibration to contour
    transformed_outline = affc.affine_transform_contour_dtc(
        transformed_outline)

    # apply offset and scale to contour
    transformed_outline[0, :] = transformed_outline[0, :] * scale[0]
    transformed_outline[1, :] = transformed_outline[1, :] * scale[1]

    transformed_outline[0, :] = transformed_outline[0, :] + offset[0]
    transformed_outline[1, :] = transformed_outline[1, :] + offset[1]

    outline = outline.transpose().reshape((-1, 1, 2))
    transformed_outline = transformed_outline.transpose().reshape((-1, 1, 2))

    return outline.astype(int), transformed_outline.astype(int)


def images_and_outline(background, scale, offset, contour_on_rgb=True):
    ''' Capture depth and color input and find the contour.
        Transform the contour to match the color image.
        Return copy on color input, rgb image representing the depth and
        the transformed contour '''

    capture_depth = measure_depth()
    rgb_frame = np.copy(get_video())

    clean_depth = remove_background(capture_depth, background)
    contour = normalised_depth_to_contour(clean_depth)
    outline, transformed_outline = transform_contour(
        contour, scale, offset)

    # set rgb image visible
    depthimage = depth_to_depthimage(capture_depth)

    # add contour to images
    cv2.drawContours(depthimage, [outline], -1, (0, 0, 255), 2)

    if contour_on_rgb:
        cv2.drawContours(rgb_frame, [transformed_outline], -1,
                (0, 0, 255), 2)

    return rgb_frame, depthimage, outline