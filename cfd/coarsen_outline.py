
import os
import numpy as np

coords1 = np.loadtxt('test1-outline-coords-old.dat')

num_points=len(coords1)

new_outline_file = open("test1-outline-coords.dat", "w")


for i in range(num_points):
    if( i % 5 == 0):
        new_outline_file.write("%10.6f \t %10.6f \n" % (coords1[i,0], coords1[i,1]) )

new_outline_file.close()
