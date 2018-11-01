from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import numpy as np
from matplotlib_widget import PlotCanvas
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import cv2, sys


def vtkfile_to_numpy(filename, nprocs):
    # Open the file with read only permit
    vtkfile = open(filename, "r")

    # Header
    line = vtkfile.readline()
    # Project name
    line = vtkfile.readline()
    # ASCII or Binary
    line = vtkfile.readline()
    # Grid type
    line = vtkfile.readline()
    # Points
    line = vtkfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    numpoints = int(listtemp[1])
    print("numpoints=", numpoints)
    # Point coordinates
    coords = np.zeros((numpoints, 3), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        coords[ii, 0] = float(listtemp[0])
        coords[ii, 1] = float(listtemp[1])
        coords[ii, 2] = float(listtemp[2])

    # Elements(Cells)
    line = vtkfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    numcells = int(listtemp[1])
    print("numcells=", numcells)
    # Elements connectivity
    elems = np.zeros((numcells, 3), dtype=int)
    for ii in range(numcells):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        elems[ii, 0] = int(listtemp[1])
        elems[ii, 1] = int(listtemp[2])
        elems[ii, 2] = int(listtemp[3])

    # CELL_TYPES
    line = vtkfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    iii = int(listtemp[1])
    for ii in range(iii):
        line = vtkfile.readline()

    if (nprocs > 1):
        # CELL DATA - coloring
        line = vtkfile.readline()
        line = vtkfile.readline()
        line = vtkfile.readline()
        for ii in range(numcells):
            line = vtkfile.readline()

    # Point data
    line = vtkfile.readline()
    line = vtkfile.readline()
    line = vtkfile.readline()

    # Pressure
    pressure = np.zeros((numpoints, 1), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        pressure[ii, 0] = float(listtemp[0])

    # Velocity
    line = vtkfile.readline()

    velocity = np.zeros((numpoints, 3), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        velocity[ii, 0] = float(listtemp[0])
        velocity[ii, 1] = float(listtemp[1])
        velocity[ii, 2] = float(listtemp[2])

    vtkfile.close()

    return coords, elems, velocity


def plot(canvas,
         coords,
         elems,
         velocity,
         dotri,
         dovector,
         docontour,
         subject_image,
         velo_magn_max=None):

    fig = canvas.figure
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    xplotlims = (min(coords[:, 0]), max(coords[:, 0]))
    yplotlims = (min(coords[:, 1]), max(coords[:, 1]))

    if subject_image is not None:
        xplotlim_m = max(min(coords[:, 0]), 0)
        xplotlim_p = min(max(coords[:, 0]), subject_image.shape[1])

        yplotlim_m = max(min(coords[:, 1]), 0)
        yplotlim_p = min(max(coords[:, 1]), subject_image.shape[0])

        xplotlims = (xplotlim_m, xplotlim_p)
        yplotlims = (yplotlim_m, yplotlim_p)
    else:
        xplotlims = (min(coords[:, 0]), max(coords[:, 0]))
        yplotlims = (min(coords[:, 1]), max(coords[:, 1]))

    ax.set_xlim(xplotlims)
    ax.set_ylim(yplotlims)

    # In any case we plot the mesh
    if dotri:
        ax.triplot(
            coords[:, 0], coords[:, 1], elems, color='red', linewidth=0.4)

    if docontour:
        velocity_magn = np.hypot(velocity[:, 0], velocity[:, 1])
        if velo_magn_max is None:
            velo_magn_max = velocity_magn.max()
        VV = np.linspace(0.0, velo_magn_max, 20)

        mappable = ax.tricontourf(coords[:,0], coords[:,1], elems, \
                velocity_magn, VV, cmap="rainbow", extend='both')

        # this must go on another picture or it breaks the reference frame for
        # the subject image
        # plt.figure(
        # plt.colorbar(mappable)
        # all the operations to save the colorbar in another picture

    if dovector:
        ax.quiver(
            coords[:, 0],
            coords[:, 1],
            velocity[:, 0],
            velocity[:, 1],
            angles='xy',
            scale_units='xy',
            color='lightgreen',
            width=0.005,
            scale=0.0325)

    fig.canvas.draw()

    if subject_image is not None:
        #https://matplotlib.org/gallery/misc/agg_buffer_to_array.html
        #subject_image = subject_image[:, :, [0, 1, 2]]
        M = np.float32([[1, 0, 0], [0, -1, subject_image.shape[0]]])

        dypx, dxpx, _ = np.array(fig.canvas.renderer._renderer).shape
        subject_layer = cv2.warpAffine(subject_image, M, (dxpx, dypx))

        ax.imshow(subject_layer)

    return np.array(fig.canvas.renderer._renderer)


def vtk_to_plot(canvas, vtk_filename, nprocs, dotri,dovector,docontour,subject_image,\
        velocity_magn=None):

    coords, elems, velocity = vtkfile_to_numpy(vtk_filename, nprocs)
    return plot(canvas, coords, elems, velocity, dotri, dovector, docontour,
                subject_image, velocity_magn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = PlotCanvas()
    vtk_file = 'outbox/testrun1/elmeroutput0001.vtk'
    image_file = 'outbox/testrun1/kinect/scf1-fullcolorimage.png'
    image = plt.imread(image_file)
    vtk_to_plot(canvas, vtk_file, 1, False, True, False, image)
    canvas.show()
    sys.exit(app.exec_())
