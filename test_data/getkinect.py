from freenect import sync_get_depth as get_depth, sync_get_video as get_video
from freenect import DEPTH_MM
import numpy as np
import time
import matplotlib.pyplot as plt

depth = []
color = []
for i in range(30):
    print(i)
    (d,_) = get_depth(format=DEPTH_MM)
    (rgb,_) = get_video()
    depth.append(np.array(d))
    color.append(np.array(rgb))
    time.sleep(0.3)

np.save("kinect_data.npy", np.array(depth))
np.save("color_kinect_data.npy", np.array(color))

