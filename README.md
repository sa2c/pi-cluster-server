# User Interface for the Raspberry Pi Cluster

This is the GUI for the airflow simulation demonstration
on the Rapsberry Pi cluster. It is used to capture a colour
image and a contour with a Kinect camera and to submit the
contour to a cluster running the Cluster Queue in his
repository. The cluster queue will run a 2d airflow simulation
and produce vector plots of the resutlts.
The GUI will then display the results and allow printing a
postcard with the results.

The cluster can also be controlled using the python Controller
class found in controller.py.

## Installation

### Installing freenect for python3

We use the freenect library to communicate with the Kinect
camera. To install it, first clone the repository
```
git clone https://github.com/OpenKinect/libfreenect
cd libfreenect
```
Create a build directory for cmake
```
mkdir build
cd build
```
Build and install
```
make
sudo make install
```

You can use ```freenect-glview``` or ```freenect-camtest```

In addition to the library itself, you need the python wrapper.
Go to the wrappers folder and install with pip
```
cd ..
cd wrappers/python
python3 -m pip install .
```

### Python Dependencies

Other python dependencies can be installed with
```
python3 -m pip install -r requirements.txt
```

### Settings

All settings you need to edit are in settings.py.
There you can set the following
| Variable | |
|-------------|------------------------------|
| cluster_address | Network address to the node where the cluster queue is running. |
| cluster_path | the path to the cluster queue |
| mock_kinect | Set to False unless you want to use the mock feed. |
| dmin | The minimum distance shown in the depth image in mm. |
| dmax | The maximum distance shown in the depth image in mm. |
| min_distance | The distance threshold used in capturing the contour as an integer out of 255. |
| num_points | The number of points in the contour |
| nmeasurements | Number of measurements used to produce the depth image. A higher number results in a smoother image, but if the subject does not stay still, produces weird effects |
| corner_cutting_steps | How many times to run a smoothing algorithm on the contour. |
| color_scale | Initial color adjustment for the display. |
| flip_display_axis | Wether to flip the image along the vertical axis. |
| local_path | Path to the ui. |
| nprocs | Number of processes to use locally for calculating the drag. |


## Running the UI

To run the UI simply type
```
python3 ui.py
```

At the beginning the UI will detect if a kinect is present.
If you don't have one plugged in or you don't have the freenect libary,
it will not show a video feed, but you can display finished simulations
and the queue.
