
from freenect import sync_get_depth as get_depth, sync_get_video as get_video

import cv2
import numpy as np

print("Getting frame")

# Remove small distance results, these are out of range
def threshold(d,cutoff = 1024):
    return d*(d<cutoff) + 2047*(d>=cutoff)

measures = 1

(depth,_), (video,_) = get_depth(), get_video()
depth = threshold(depth) / measures
for m in range(1,measures):
   (_d,_) = get_depth()
   _d = threshold(_d)/measures
   depth += _d

print("Converting to bitmap")
depth = np.dstack((depth,depth,depth)).astype(np.uint8)
gray = cv2.cvtColor(depth,cv2.COLOR_BGR2GRAY)

cv2.imwrite("depthimage.bmp", gray)

# Threshold
ret, thresholded = cv2.threshold(gray,124,255,cv2.THRESH_BINARY_INV)
cv2.imwrite("thresholded.bmp",thresholded)

print("Finding contour")
contours, hierarchies = cv2.findContours(thresholded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
contour = max(contours, key=cv2.contourArea)

outline = contour[:,0,:]
np.savetxt("contour.txt", outline, fmt='%i %i')

# Draw the outline into an image
cv2.drawContours(depth, contour, -1, (0,0,255), 2)
cv2.imwrite("contours.bmp",depth)



