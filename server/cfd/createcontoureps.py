#ioff()
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import model
import postplotting as post
from matplotlib_to_image import fig2img


def generate_velocityvectorplots_from_vtk(filename, compute_bound, nprocs):
    global velo_magn_max

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
    velocity_magn = np.zeros((numpoints, 1), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        velocity[ii, 0] = float(listtemp[0])
        velocity[ii, 1] = float(listtemp[1])
        velocity[ii, 2] = float(listtemp[2])
        velocity_magn[ii, 0] = np.abs(velocity[ii, 0] * velocity[ii, 0] +
                                      velocity[ii, 1] * velocity[ii, 1])

    vtkfile.close()

    if (compute_bound == True):
        velo_magn_max = np.max(velocity_magn[:, 0])
    VV = np.linspace(0.0, velo_magn_max, 20)

    # generate images

    fname_data = filename.split(".")
    # Velocity magnitude contour plot

    contourplots = True
    vectorplots = True

    if (contourplots == True):
        # https://matplotlib.org/gallery/misc/agg_buffer_to_array.html
        fig1 = plt.figure(1)
        ax1 = fig1.add_subplot(111)
        ax1.triplot(coords[:, 0],
                    coords[:, 1],
                    elems,
                    color='black',
                    linewidth=0.2)
        mappable = ax1.tricontourf(coords[:, 0],
                                   coords[:, 1],
                                   elems,
                                   velocity_magn[:, 0],
                                   VV,
                                   cmap="rainbow",
                                   extend='both')
        plt.colorbar(mappable)
        ax1.axis('off')
        ax1.axes.set_aspect(1.0)
        fig1.canvas.draw()

        outfile = fname_data[0] + "-velomagn.png"
        fig1.savefig(outfile, dpi=200)
        plt.close()

    if (vectorplots == True):
        # Quiver plot
        fig2 = plt.figure(2)
        ax2 = fig2.add_subplot(111)
        ax2.quiver(coords[:, 0],
                   coords[:, 1],
                   velocity[:, 0],
                   velocity[:, 1],
                   angles='xy',
                   scale_units='xy')
        ax2.triplot(coords[:, 0],
                    coords[:, 1],
                    elems,
                    color='black',
                    linewidth=0.2)
        ax2.axes.set_aspect(1.0)
        ax2.axis('off')
        #plt.show()
        outfile = fname_data[0] + "-quiver.png"
        fig2.savefig(outfile, dpi=200)
        plt.close()

    return


######################################################


# save a gif from a list of PIL images
def save_gif(filename, images):
    if images[0] is None:
        print("NO image to write to {filename} (image is None)".format(filename=filename))
    else:
        print('writing image: {filename}'.format(filename=filename))
        images[0].save(filename,
                       save_all=True,
                       append_images=images[1:],
                       duration=500,
                       loop=0)


# Generates the images for all the time steps requested #
def generate_images_vtk(sim_id, nprocs, num_timesteps):
    """
    Generates gif images for display on screen. The images are (cryptically) called
    named left.gif and right.gif
    """
    sim = model.get_simulation(sim_id)

    if sim is not None:
        if 'rgb' in sim:
            rgb = sim['rgb']
        else:
            rgb = None

    fig = plt.figure()

    simdir = model.run_directory(sim_id) + '/'

    images_left = [
        generate_single_vtk_plot(fig, i, sim_id, nprocs, False, True, False,
                                 rgb) for i in range(1, 11)
    ]
    save_gif(simdir + 'left.gif', images_left)

    images_right = [
        generate_single_vtk_plot(fig, i, sim_id, nprocs, True, False, True,
                                 rgb) for i in range(1, 11)
    ]
    save_gif(simdir + 'right.gif', images_right)

    return


def generate_single_vtk_plot(fig,
                             index,
                             sim_id,
                             nprocs,
                             dotri,
                             dovector,
                             docontour,
                             image=None,
                             velocity_magn=None):

    vtk_filename = model.run_directory(
        sim_id) + "/" + 'elmeroutput{index:04}.vtk'.format(index=index)

    fig.clear()

    if (os.path.isfile(vtk_filename) == True):
        post.vtk_to_plot(fig.canvas, vtk_filename, nprocs, dotri, dovector,
                         docontour, image, velocity_magn)
        im = fig2img(fig)
        return im
    else:
        print("{} file does not exist".format(vtk_filename))


##################################################
##################################################
