import os
from tempfile import mkdtemp

# Mock Kinect
mock_kinect = True

# Kinect depth data settigs
dmin = 1000
dmax = 3000
min_distance = 230  # out of 255

# Settings related to the contour estimation
num_points = 100
nmeasurements = 5
corner_cutting_steps = 50

# Image display adjustments
color_scale = [1, 1, 0.8]
flip_display_axis = True

# Cluster settings
cluster_address = "localhost"
cluster_path = os.environ['PWD']+'/../cluster_queue'

# Local settings
local_path = os.environ['PWD']
nprocs = 1

