import os
import numpy as np


def get_drag_from_file(project_name):
    global drag
    dst="./" + project_name + "/mesh/"
    os.chdir(dst)

    fname = project_name + "-drag.dat"

    # Open the file with read only permit
    dragfile = open(fname, "r")

    # Header
    line = dragfile.readline()

    drag_list=[]

    # First time step
    line = dragfile.readline()
    while(line != ''):
        listtemp = " ".join(line.split())
        listtemp = listtemp.split(" ")
        drag_list.append(float(listtemp[1]))
        line = dragfile.readline()

    drag = drag_list[len(drag_list)-1]

    dragfile.close()

    return




global drag
drag=0.0
get_drag_from_file("test2")
print("Drag is %f " % drag)