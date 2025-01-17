import os
import numpy as np
import random
from shapely.geometry import Point
from shapely.geometry import Polygon
import settings
#import matplotlib.pyplot as plt

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import model


# Generates a random point inside a polygon
#
def get_random_point_in_polygon(poly):
    (minx, miny, maxx, maxy) = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


##################################################
##################################################


# Generates the polyline file from the outline
#
def generate_polyline_from_outline(sim_id, domain_area):

    # Read the coordinates of the points on the outline
    ##
    outline_coords_fname = model.outline_coords_file(sim_id)
    outline_coords_file = open(outline_coords_fname, "r")

    outline_coords = np.loadtxt(outline_coords_fname)
    outline_coords_file.close()

    num_points = len(outline_coords)

    if (num_points <= 0):
        print("Number of points in the outline is zero\n")
        print("Program aborted")
        exit(302)

    #outline_coords = outline_coords[:,1:3]

    mypoly = Polygon(outline_coords)

    # Compute the bounds of the outline
    (minx, miny, maxx, maxy) = mypoly.bounds

    lenx = maxx - minx
    leny = maxy - miny

    pt1x = minx - 2.0 * lenx
    pt1y = miny - 1.0 * leny

    pt2x = maxx + 4.0 * lenx
    pt2y = maxy + 1.0 * leny

    domain_area = (pt2x - pt1x) * (pt2y - pt1y)

    # Create and write the .poly file to be used for generating the mesh

    poly_fname = '{run_dir}/simulation.poly'.format(
        run_dir=model.run_directory(sim_id))

    poly_file = open(poly_fname, "w")

    # Header - <Number of poiints> <DIM> <Flag> <Flag>
    poly_file.write("%d \t %d \t %d \t %d\n" % (num_points + 4, 2, 0, 1))

    # Channel boundary
    poly_file.write("#channel boundary\n")

    poly_file.write("%d \t %10.6f \t %10.6f \t %d\n" % (1, pt1x, pt1y, 2))
    poly_file.write("%d \t %10.6f \t %10.6f \t %d\n" % (2, pt2x, pt1y, 3))
    poly_file.write("%d \t %10.6f \t %10.6f \t %d\n" % (3, pt2x, pt2y, 2))
    poly_file.write("%d \t %10.6f \t %10.6f \t %d\n" % (4, pt1x, pt2y, 4))

    # Immersed object
    poly_file.write("#immersed object boundary\n")
    imm_body_id = 11
    for i in range(num_points):
        poly_file.write(
            "%d \t %10.6f \t %10.6f \t %d\n" %
            ((5 + i), outline_coords[i, 0], outline_coords[i, 1], imm_body_id))

    # Write edges - <count> <point #1> <point #2> <id num>
    poly_file.write("#edges\n")
    poly_file.write("%d \t %d \n" % (num_points + 4, 1))
    poly_file.write("#channel boundary\n")
    poly_file.write("%d \t %d \t %d \t %d\n" % (1, 1, 2, 2))
    poly_file.write("%d \t %d \t %d \t %d\n" % (2, 2, 3, 3))
    poly_file.write("%d \t %d \t %d \t %d\n" % (3, 3, 4, 2))
    poly_file.write("%d \t %d \t %d \t %d\n" % (4, 4, 1, 4))

    poly_file.write("#immersed object boundary\n")
    imm_body_id = 11
    for i in range(num_points - 1):
        poly_file.write("%d \t %d \t %d \t %d\n" % ((5 + i), (5 + i),
                                                    (6 + i), imm_body_id))
    poly_file.write("%d \t %d \t %d \t %d\n" %
                    (num_points + 4, num_points + 4, 5, imm_body_id))

    poly_file.write("#holes\n")
    poly_file.write("1\n")
    point_in_poly = get_random_point_in_polygon(mypoly)
    poly_file.write("%d \t %10.6f \t %10.6f \n" %
                    (1, point_in_poly.x, point_in_poly.y))

    poly_file.close()

    return


##################################################
##################################################


# Generates the Finite Element mesh from the polyline file
#
def generate_mesh_from_outline(sim_id, nprocs):
    print("generate_mesh_from_outline")

    domain_area = 1.0
    generate_polyline_from_outline(sim_id, domain_area)

    project_dir = model.run_directory(sim_id)

    # generate the mesh with "triangle" library
    ###########################################

    mesh_size = domain_area / 10.0
    print("domain_area = %12.6f \n" % domain_area)
    print("mesh_size   = %12.6f \n" % mesh_size)

    mesh_size = str(mesh_size)
    mesh_size = mesh_size.lstrip('0')
    mesh_size = mesh_size.lstrip('.')

    #cmd = "./triangle-lib/triangle -pq32.0 -a0.05" + str(mesh_size) + " " + project_name
    cmd = 'cd {project_dir} && {exe} -pq32.0 -a2000 simulation'.format(
        project_dir=project_dir, exe=settings.triangle_exe)
    print('Running: ' + cmd)
    exit_code = os.system(cmd)

    if exit_code != 0:
        print("Error running {exe}".format(exe=settings.triangle_exe))
        print("Please make sure you've built the triangle binary")
        exit(1)

    # generate the mesh using ElmerGrid
    # also partition it if nprocs > 1
    ###################################

    if (nprocs == 1):
        cmd = " cd {project_dir} && ElmerGrid 11 2 simulation.1".format(
            project_dir=project_dir)
    else:
        nn = int(np.ceil(np.sqrt(nprocs)))
        cmd = "cd " + project_dir + " && ElmerGrid 11 2 simulation.1 -partition " + str(
            nn) + " " + str(nn) + " 1"

    print("Running: " + cmd)

    exit_code = os.system(cmd)

    if exit_code != 0:
        print("Error occured whilst running ElmerGrid: {cmd}".format(cmd=cmd))
        exit(1)
    return


##################################################
##################################################
