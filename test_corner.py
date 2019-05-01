import numpy as np
import cv2
from kinectlib.calibration import affine_calibration as affc

contour = np.array([[1,2],[1,3],[3,4],[2,5],[1,1]])


print( affc.affine_transform_contour_dtc(contour.transpose()) )
print( affc.affine_transform_contour_dtc(contour.transpose()) )

