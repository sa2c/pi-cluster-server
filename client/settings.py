import os
from tempfile import mkdtemp

# Mock Kinect
mock_kinect = False

# Kinect depth data settigs
min_distance = 230  # out of 255
thresholds_from_file = True

# Settings related to the contour estimation
num_points = 100
nmeasurements = 20
corner_cutting_steps = 10

# Image display adjustments
color_scale = [1, 1, 0.8]
flip_display_axis = True

# Cluster settings
cluster_address = "http://10.0.0.253:3524"

# Local settings
local_path = os.environ['PWD']
nprocs = 1


leaderboard_number = 10
