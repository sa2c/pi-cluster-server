#ioff()

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import glob

from cluster_manager import run_filepath

from settings import nprocs


def compute_drag_for_simulation(index):
    final_vtk_file = run_filepath(index, f'elmeroutput0010.vtk')

    fname_poly = run_filepath(index, f'run{index}.poly')

    if os.path.exists(fname_poly):
        return compute_drag_from_vtk(fname_poly, final_vtk_file, nprocs)
    else:
        return 9999


def compute_drag_from_vtk(fname_poly, vtkfilename, nprocs):

    # Open the file with read only permit
    vtkfile = open(vtkfilename, "r")

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
    #print "numpoints=", numpoints
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
    #print "numcells=", numcells
    for ii in range(numcells):
        line = vtkfile.readline()

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

    vtkfile.close()

    ##########
    ##
    # read the .poly file and get the points on the outline
    polyfile = open(fname_poly, "r")

    # read the first line and get the number of points on the outline
    line = polyfile.readline()
    listtemp = " ".join(line.split())
    listtemp = listtemp.split(" ")
    numpoints_outline = int(listtemp[0]) - 4
    #print "numpoints_outline", numpoints_outline
    coords_outline = np.zeros((numpoints_outline, 3), dtype=float)

    # read the next six lines
    line = polyfile.readline()
    line = polyfile.readline()
    line = polyfile.readline()
    line = polyfile.readline()
    line = polyfile.readline()
    line = polyfile.readline()

    for ii in range(numpoints_outline):
        line = polyfile.readline()
        #print("Line {}: {}".format(ii, line.strip()))
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        coords_outline[ii, 0] = float(listtemp[1])
        coords_outline[ii, 1] = float(listtemp[2])

    # Compute drag by summing pressure at all the nodes on the outline
    drag = 0.0
    for ii in range(numpoints_outline):
        xx = coords_outline[ii, 0]
        yy = coords_outline[ii, 0]

        for jj in range(numpoints):
            if ((abs(xx - coords[jj, 0]) < 1.0e-6)
                    and (abs(yy - coords[jj, 0]) < 1.0e-6)):
                drag = drag + pressure[jj, 0]
                break

    polyfile.close()

    return drag


######################################################


# Compute drag from the pressure at the nodes on the outline
#
def compute_drag(project_name, nprocs, num_timesteps):
    #print("The dir is: %s", os.getcwd())

    fname_temp = "elmeroutput"
    global drag

    filename_drag = project_name + "-drag.dat"
    dragfile = open(filename_drag, "w")

    dragfile.write("FileCount \t Dragforce \n")

    drag_list = np.zeros(num_timesteps, dtype=float)
    count = 0
    for fnum in range(num_timesteps):
        vtkfilename = fname_temp + str(fnum + 1).zfill(4) + ".vtk"
        #print vtkfilename
        if (os.path.isfile(vtkfilename) == True):
            compute_drag_from_vtk(project_name, vtkfilename, nprocs)
            drag = -drag
            drag_list[fnum] = drag
            #print("FileCount=%04d \t Dragforce=%12.6f \n" % ((fnum+1), drag))
            dragfile.write("%04d \t %12.6f \n" % ((fnum + 1), drag))
            count = count + 1

    plt.figure(1)
    xval = np.linspace(2, count, count - 1)
    yval = drag_list[1:count]
    plt.plot(xval, yval, 'k', linewidth=1)
    #plt.axes().set_aspect(1.0)
    #plt.xlim(1,count)
    #plt.ylim(0,np.ceil(yval[min(5,count)]))
    plt.xlabel("Time step")
    plt.ylabel("Drag force")
    outfile = project_name + "-dragforce.png"
    plt.savefig(outfile, dpi=200)
    plt.close()

    return


##################################################
##################################################
