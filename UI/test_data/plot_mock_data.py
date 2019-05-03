from freenect import sync_get_depth as get_depth, sync_get_video as get_video
from freenect import DEPTH_MM
import numpy as np
import matplotlib.pyplot as plt
import time

color = np.load("color_kinect_data.npy")
for i in range(30):
    print(i)
    plt.imshow(color[i])
    plt.show()
