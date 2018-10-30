#ioff()

import sys
import os
import matplotlib.pyplot as plt
import numpy as np


def generate_velocityvectorplots_from_vtk(filename, compute_bound):
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
    #print listtemp
    numpoints = int(listtemp[1])
    #print "numpoints=", numpoints
    # Point coordinates
    coords = np.zeros((numpoints,3), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        coords[ii,0] = float(listtemp[0])
        coords[ii,1] = float(listtemp[1])
        coords[ii,2] = float(listtemp[2])

    # Elements(Cells)
    line = vtkfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    #print listtemp
    numcells = int(listtemp[1])
    #print "numcells=", numcells
    # Elements connectivity
    elems = np.zeros((numcells,3), dtype=int)
    for ii in range(numcells):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        elems[ii,0] = int(listtemp[1])
        elems[ii,1] = int(listtemp[2])
        elems[ii,2] = int(listtemp[3])

    # CELL_TYPES
    line = vtkfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    iii = int(listtemp[1])
    for ii in range(iii):
        line = vtkfile.readline()

    # Point data
    line = vtkfile.readline()
    line = vtkfile.readline()
    line = vtkfile.readline()

    # Pressure
    pressure = np.zeros((numpoints,1), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        pressure[ii,0] = float(listtemp[0])

    # Velocity
    line = vtkfile.readline()

    velocity = np.zeros((numpoints,3), dtype=float)
    velocity_magn = np.zeros((numpoints,1), dtype=float)
    for ii in range(numpoints):
        line = vtkfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        velocity[ii,0] = float(listtemp[0])
        velocity[ii,1] = float(listtemp[1])
        velocity[ii,2] = float(listtemp[2])
        velocity_magn[ii,0] = np.abs(velocity[ii,0]*velocity[ii,0]+velocity[ii,1]*velocity[ii,1])

    vtkfile.close()

    if(compute_bound == True):
        velo_magn_max = 0.75*np.max(velocity_magn[:,0])
    VV=np.linspace(0.0, velo_magn_max, 20)

    # generate images

    fname_data = filename.split(".")
    # Velocity magnitude contour plot

    veloplots = False
    vectorplots = True

    if(veloplots == True):
        plt.figure(1)
        plt.triplot(coords[:,0], coords[:,1], elems, color='black', linewidth=0.2)
        plt.tricontourf(coords[:,0], coords[:,1], elems, velocity_magn[:,0], VV, cmap="rainbow", extend='both')
        plt.colorbar()
        plt.axis('off')
        plt.axes().set_aspect(1.0)
        outfile = fname_data[0]+"-velomagn.png"
        plt.savefig(outfile, dpi=200)
        plt.close()

    if(vectorplots == True):
        # Quiver plot
        plt.figure(2)
        plt.quiver(coords[:,0], coords[:,1], velocity[:,0], velocity[:,1], angles='xy', scale_units='xy')
        plt.triplot(coords[:,0], coords[:,1], elems, color='black', linewidth=0.2)
        plt.axes().set_aspect(1.0)
        plt.axis('off')
        #plt.show()
        outfile = fname_data[0]+"-quiver.png"
        plt.savefig(outfile, dpi=200)
        plt.close()

    return
######################################################

# Generates the images for all the time steps requested
#
def step6_generate_images_vtk(project_name, if_serial, num_timesteps):
    #print("Loading ", filename_prefix)

    print("The dir is: %s", os.getcwd())
    #dst="./" + project_name + "/mesh/"
    #dst="./mesh/"
    #os.chdir(dst)

    fname_temp="elmeroutput"
    global velo_magn_max

    if if_serial:
        for fnum in range(num_timesteps):
            filename = fname_temp + str(fnum+1).zfill(4) + ".vtk"
            generate_velocityvectorplots_from_vtk(filename, (fnum == 0))
            print(filename)
    else:
        filename_prefix=test.vtk
    
        for fnum in range(num_timesteps):
            filename = filename_prefix + "." + str(fnum-1).zfill(4)
            generate_velocityvectorplots_from_vtk(filename, (fnum ==0))

    return
##################################################
##################################################

