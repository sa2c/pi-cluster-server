import numpy as np
from matplotlib import pyplot as plt
import cv2

# NUMBERS TO TWEAK (ONCE), ALSO SIGN! 
kinect_xfov_radians = 1.0821 # 62 degrees
kinect_xres = 640
kinect_sensor_camera_distance_mm = 50.0 # sign to adjust 
kinect_sensor_camera_deltaphi_pixel = 0 # sign to adjust 

def get_larges_contour(depth_img,threshold):
    _,thresholded = cv2.threshold(depth_img,threshold,1,cv2.THRESH_BINARY)

    _,contours,hierarchy = cv2.findContours(
            np.array(thresholded,dtype=np.uint8),cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE)

    contour = max(contours, key=cv2.contourArea)

    return contour
    

def compute_shift(depth_img,contour):
    # computing mean distance in the contour
    area = cv2.contourArea(contour)
    cropped_distance=select_image_inside(depth_img,contour)
    mean_distance_mm = cropped_distance.sum()/area

    print(f"Mean distance is: {mean_distance_mm} mm")

    # parallax shift for the contour is only along x axis.
    # should be sensor-camera distance /(field of view in radians/ no of pixel)
    # sensor-camera distance must be in the same unit as the distance measured
    # by the sensor
    factor = kinect_sensor_camera_distance_mm/(np.sin(kinect_xfov_radians/2)/(kinect_xres/2))
    xshift = factor/mean_distance_mm + kinect_sensor_camera_deltaphi_pixel

    print(f"x-shift is: {xshift}")
    return xshift

def select_image_inside(img,contour):
    ones = np.ones_like(img)
    outside = cv2.drawContours(ones,[contour],0,(0),-1)
    mask = np.ones_like(img)-outside
    return img*mask


def cropped_color_subject(color_img, depth_img,contour):
    '''
    Aim:
        obtain a proper cropped version of the subject color image.
    Method:
        we get the contour of the subject from the depth image. The color image 
        is shifted compared to the depth image, and the amount of the shift 
        depends on the position in the image. If we had depth information for 
        all pixels it would be possible to compute the shift and do a opencv 
        inverseWarp, but unfortunately the depth information is missing for 
        reflecting surfaces, and it is quite noisy.  
        We can, though, recover the averavge depth inside the contour, assuming
        that it is more or less constant, and from that compute the parallax
        and then shift the color image so that it matches the depth image.
    '''

    xshift = compute_shift(depth_img,contour)

    # we shift the contour...

    shifted_contour = np.copy(contour)
    shifted_contour[:,0] += int(xshift)

    # ... get the cropped rgb image with the shifted contour ...
    cropped_rgb_shifted = select_image_inside(color_img,shifted_contour)

    # creating alpha channel
    alpha_channel = np.ones_like(cropped_rgb_shifted,dtype=np.uint8)*255
    alpha_channel = select_image_inside(alpha_channel,shifted_contour)

    r_channel,g_channel,b_channel = cv2.split(img)
    cropped_rgba_shifted = cv2.merge((r_channel,g_channel,
        b_channel,alpha_channel))

    # and shift again back the cropped rgb image
    maxx_s,minx_s = shifted_contour[:,0].max(), shifted_contour[:,0].min()
    maxy,miny = contour[:,1].max(), contour[:,1].min()

    cropped_rgba = cropped_rgba_shifted[minx_s:maxx_s+1,miny:maxy+1]

    subject_limits = ((minx,maxx+1),(miny,maxy+1))

    return cropped_rgba,subject_limits







