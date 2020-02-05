from freenect import sync_get_depth as get_depth, sync_get_video as get_video
from freenect import DEPTH_MM
import numpy as np
import sys

n_frames = 1000
if len(sys.argv) > 1:
    n_frames = int(sys.argv[1])

if __name__ == "__main__":
    ''' Record data from Kinect device to use for mocking the device'''
    depth_images = []
    color_images = []
    print('start')
    for i in range(n_frames):
        print(f"Step {i} of {n_frames}, please wait...")
        (depth, _) = get_depth(format=DEPTH_MM)
        (rgb, _) = get_video()
        depth_images.append(np.copy(depth))
        color_images.append(np.copy(rgb))

    print('finished, saving')

    depth_images = np.array(depth_images)
    color_images = np.array(color_images)
    np.save("kinect_data.npy", depth_images)
    np.save("color_kinect_data.npy", color_images)
    print('done')
