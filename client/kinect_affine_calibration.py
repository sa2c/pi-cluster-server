# coding: utf-8
import numpy as np
from matplotlib import pyplot as plt
import cv2

#_dtcfile = 'calibration/depth_to_color_calibration_points.dat'
_dtcfile ='./kinectlib/calibration/depth_to_color_calibration_points.dat'
_calibration_dtc_M = None
_x_flip = True

def _calcAffineTransform_dtc(dtcfile_t):
    dtc = np.loadtxt(dtcfile_t, dtype=np.float32)
    global _x_flip
    if _x_flip:
        dtc[:,0] = 640 - dtc[:,0]
        dtc[:,2] = 640 - dtc[:,2]
    color_points = dtc[:, [2, 3]]
    depth_points = dtc[:, [0, 1]]
    M = cv2.getAffineTransform(depth_points, color_points)
    
    return M

def affine_transform_contour_dtc(contour):
    #contour is a 2D array [2xN]
    #M is a 2D array [2x3]

    contour3 = np.vstack((contour,np.ones_like(contour[0,:])))

    global _calibration_dtc_M
    if _calibration_dtc_M is None:
        _calibration_dtc_M = _calcAffineTransform_dtc(_dtcfile)

    return np.matmul(_calibration_dtc_M,contour3)[0:2,:]


if __name__ == '__main__':
    compute = False
    
    # depth
    if compute:
        kd = np.load('kinect_data.npy')
        kdf = np.array(kd, dtype=np.float)
    
        zeros = kd == 0
        zeros = zeros.sum(axis=0)
        skdf = np.sum(kdf, axis=0)
    
        kdavg = skdf / (zeros.max() - zeros + 1)
    
        kdavgui8 = np.array((kdavg / kdavg.max()) * 255, dtype=np.uint8)
        a = np.ones_like(kdavgui8) * 127
        kdavgui8rgba = cv2.merge((kdavgui8, kdavgui8, kdavgui8, a))
    
        np.save('kinect_depth_averages_rgba.npy', kdavgui8rgba)
    else:
        kdavgui8rgba = np.load('kinect_depth_averages_rgba.npy')
    
    # color
    
    if compute:
        ckd = np.load('color_kinect_data.npy')
        ckdavg = np.average(ckd, axis=0)
    
        ckdavgui8 = np.array(ckdavg, dtype=np.uint8)
    
        r, g, b = cv2.split(ckdavgui8)
        a = np.ones_like(r) * 127
        ckdavgui8rgba = cv2.merge((r, g, b, a))
        np.save('kinect_color_averages_rgba.npy', ckdavgui8rgba)
    else:
        ckdavgui8rgba = np.load('kinect_color_averages_rgba.npy')
    
    a = np.ones_like(ckdavgui8rgba[:, :, 0]) * 127
    
    M = calcAffineTransform_dtc(dtcfile)
    
    warpedkdavgui8rgba = cv2.warpAffine(
        kdavgui8rgba, M, (ckdavgui8rgba.shape[1], ckdavgui8rgba.shape[0]))
    
    plt.imshow(ckdavgui8rgba)
    plt.imshow(warpedkdavgui8rgba)
    plt.show()
