import numpy as np
import matplotlib.pyplot as plt
import time

color = np.load("color_kinect_data.npy")
for i in range(30):
    print(i)
    plt.imshow(color[i])
    plt.show()
