import pytest
import settings

# Always use the mock in tests
settings.mock_kinect = True

import kinectlib.kinectlib as kinect
import numpy as np


class TestKinectLib(object):

    def setup(self):
        kinect.setup_mock()

    def test_get_depth(self):
        ''' Get_depth should return a black and white image '''
        depth = kinect.get_depth()
        assert depth.shape == (480, 640)
    
    def test_get_video(self):
        ''' Get_video should return a color image '''
        rgb = kinect.get_video()
        assert rgb.shape == (480, 640, 3)

    def test_get_mock_depth(self):
        ''' Get_depth should return a black and white image '''
        depth = kinect.get_mock_depth()
        assert depth.shape == (480, 640)
    
    def test_get_mock_background_depth(self):
        ''' The background mock should be a black and white image
            that is different from the depth mock image '''
        background_depth = kinect.get_mock_background_depth()
        assert background_depth.shape == (480, 640)

        depth = kinect.get_mock_depth()
        diff_norm = np.linalg.norm(depth - background_depth)

        assert diff_norm > 0

    def test_get_mock_video(self):
        ''' Get_video should return a color image '''
        rgb = kinect.get_mock_video()
        assert rgb.shape == (480, 640, 3)

    def test_invert_color_order(self):
        ''' '''
        rgb = kinect.get_mock_video()
        rgb[1, 1, 0] = 1
        rgb[1, 1, 1] = 2
        rgb[1, 1, 2] = 3
        bgr = kinect.invert_color_order(rgb)
        assert bgr[1, 1, 0] == 3
        assert bgr[1, 1, 1] == 2
        assert bgr[1, 1, 2] == 1

    def test_color_scale(self):
        ''' '''
        color_scale = settings.color_scale
        kinect_scale = kinect.get_color_scale()
        assert color_scale == kinect_scale

        kinect.set_color_scale([1, 2, 3])
        kinect_scale = kinect.get_color_scale()
        assert kinect_scale == [1, 2, 3]

    def test_treshold(self):
        ''' Threshold should set the maximum to 255 and minimum to 0.
            Shape should be unchanged. '''
        depth = kinect.get_mock_depth()
        depth = kinect.threshold(depth)

        assert depth.shape == (480, 640)
        assert depth.max() == 255
        assert depth.min() == 0

    def test_measure_depth(self):
        ''' Should return a thresholded image '''
        depth = kinect.measure_depth(n=settings.nmeasurements)

        assert depth.shape == (480, 640)
        assert depth.max() == 255
        assert depth.min() == 0

    def test_remove_background(self):
        ''' Returns an image with anything above -3 set to 254 '''
        depth = kinect.get_mock_depth()
        background_depth = kinect.get_mock_background_depth()

        depth = kinect.remove_background(depth, background_depth)

        assert depth.shape == (480, 640)
        assert depth.max() == 254

    def test_depth_to_depthimage(self):
        ''' Maps depth into a color image '''
        depth = kinect.get_mock_depth()
        depthimage = kinect.depth_to_depthimage(depth)

        assert depthimage.shape == (480, 640, 3)

    def test_normalised_depth_to_contour(self):
        ''' Finds the largest contour '''
        depth = kinect.get_mock_depth()
        depth = kinect.threshold(depth)
        background_depth = kinect.get_mock_background_depth()
        background_depth = kinect.threshold(background_depth)

        clean_depth = kinect.remove_background(depth, background_depth)
        contour = kinect.normalised_depth_to_contour(clean_depth)

        assert contour.ndim == 3
        assert contour.shape[1] == 1
        assert contour.shape[2] == 2

    def test_cut_corners(self):
        ''' Cut corners in an outline '''
        contour = np.array([[[0, 0]], [[0, 1]], [[1, 1]], [[1, 0]]])
        contour = kinect.cut_corners(contour, n=1)

        result = np.array([[[0, 0.5]], [[0.5, 1]], [[1, 0.5]], [[0.5, 0]]])

        assert np.array_equal(contour, result)
        
    def test_transform_contour(self):
        ''' Process the a contour into a smoothed outline '''
        contour = np.array([[[0, 0]], [[0, 50]], [[50, 50]], [[50, 0]]])
        scale = [0.5, 0.25]
        offset = [1, 2]
        outline, transformed_outline = kinect.transform_contour(contour, scale, offset)

        assert outline.ndim == 3
        assert outline.shape[0] == settings.num_points
        assert outline.shape[1] == 1
        assert outline.shape[2] == 2

        assert transformed_outline.ndim == 3
        assert transformed_outline.shape[0] == settings.num_points
        assert transformed_outline.shape[1] == 1
        assert transformed_outline.shape[2] == 2

    def test_images_and_outline(self):
        ''' Use the kinect to get the depth and color images and to
            produce the outline. '''
        # Get the background
        background_depth = kinect.get_mock_background_depth()
        background_depth = kinect.threshold(background_depth)
        scale = [1.0, 1.0]
        offset = [0, 0]

        # Wind the mock forward. It should contain an object by frame 20
        kinect.mock_kinect_index = 20

        rgb_frame, rgb_frame_with_outline, depthimage, outline = kinect.images_and_outline(background_depth, scale, offset)

        assert rgb_frame.shape == (480, 640, 3)
        assert rgb_frame_with_outline.shape == (480, 640, 3)
        assert depthimage.shape == (480, 640, 3)
        assert outline.shape == (settings.num_points, 1, 2)
