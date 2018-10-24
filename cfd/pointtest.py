##################################################################
#
# This program tests if a point lies inside a polygon
#
# Author: Dr Chennakesava Kadapa
# Date: 23-Oct-2018
#
##################################################################

import numpy as np
import random
from shapely.geometry import Point
from shapely.geometry import Polygon
#import matplotlib.pyplot as plt

#import vtk

#from vtk import vtkUnstructuredGridReader


def get_random_point_in_polygon(poly):
     (minx, miny, maxx, maxy) = poly.bounds
     while True:
         p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
         if poly.contains(p):
             return p


def get_point_inside():
    outline_coords = np.loadtxt('Ainchannel-outline-coords.dat')

    outline_coords = outline_coords[:,1:3]
    print outline_coords

    mypoly = Polygon(outline_coords)

    #x,y = mypoly.exterior.xy
    #plt.plot(x,y)

    num_points = len(outline_coords)

    if(num_points <=0):
        print("Number of points in the outline is zero\n")
        print("Program aborted")
        exit(302)

    # Compute the centroid and minimum and maxium coordinates in the outline
    min_xcoord = min(outline_coords[:,0])
    min_ycoord = min(outline_coords[:,1])
    max_xcoord = max(outline_coords[:,0])
    max_ycoord = max(outline_coords[:,1])

    (minx, miny, maxx, maxy) = mypoly.bounds

    print("bounds")
    print(min_xcoord, minx)
    print(min_ycoord, miny)
    print(max_xcoord, maxx)
    print(max_ycoord, maxy)

    length_xdir = max_xcoord - min_xcoord
    length_ydir = max_ycoord - min_ycoord

    centroid_xcoord=0.0
    centroid_ycoord=0.0
    for i in range(num_points):
        centroid_xcoord = centroid_xcoord + outline_coords[i,0]
        centroid_ycoord = centroid_ycoord + outline_coords[i,1]
        #print("%10.6f \t %10.6f \n" % (outline_coords[i,0], outline_coords[i,1]))

    pt_centroid = Point(centroid_xcoord, centroid_ycoord)

    point_in_poly = get_random_point_in_polygon(mypoly)
    print(mypoly.contains(point_in_poly))

    return
######################################



if __name__ == '__main__':
    get_point_inside()








