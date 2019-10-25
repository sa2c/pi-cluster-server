#!/usr/bin/python3
##################################################################
#
# Complete wrapper for running CFD jobs on Pi
#
# Author:    Dr Chennakesava Kadapa
# Date:      17-Oct-2018
# Copyright: @SA2C
##################################################################

#
# Step 1: Knect          -->   Depth Map
# Step 2: Depth Map      -->   Model Outline
# Step 3: Model Outline  -->   CFD Mesh
# Step 4: CFD Mesh       -->   CFD Results
# Step 5: CFD Results    -->   VTK files
# Step 6: VTK files      -->   Images
#
#
##################################################

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cfdpi_step3 import *
from cfdpi_step4 import *
from cfdpi_step5 import *
from createcontoureps import *
import computedrag
import model
import json
from images_to_pdf.pdfgen import build_sim_document

# Read the project name and other flags from the command line arguments
#

# Default entries
sim_id = "Square"
nprocs = 1

if len(sys.argv) > 1:
    sim_id = sys.argv[1]

if len(sys.argv) > 2:
    nprocs = int(sys.argv[2])

# Keep track of timings for each step
timing = {'elapsed': [], 'steps': []}

print("Starting Step 1 (Model Outline  -->  CFD Mesh)")
print("###################################################################\n")
#
# Step 1: Read the outline and generate the mesh
#
#################################################

start = time.time()
generate_mesh_from_outline(sim_id, nprocs)
end = time.time()
timing['elapsed'].append(end - start)
timing['steps'].append('Step 1: Read the outline and generate the mesh')

print("Step 1 completed successfully\n\n")
print("Starting Step 2 (CFD Mesh  -->  CFD Results)")
print("###################################################################\n")
#
# Step 2: Run Elmer with the mesh file generated in Step 1
#
##########################################################

start = time.time()
run_cfd_simulation(sim_id, nprocs)
end = time.time()
timing['elapsed'].append(end - start)
timing['steps'].append(
    'Step 2: Run Elmer with the mesh file generated in Step 1')

print("Step 2 completed successfully\n\n")
print("Starting Step 3 (CFD Results  -->  VTK files)")
print("###################################################################\n")
#
# Step 3: Create .vtk files from Elmer output
#
#####################################################

start = time.time()
generate_vtk_files(sim_id, nprocs)
end = time.time()
timing['elapsed'].append(end - start)
timing['steps'].append('Step 3: Create .vtk files from Elmer output')

print("Step 3 completed successfully\n\n")
print("Starting Step 4 (VTK files  -->  Images)")
print("###################################################################\n")
#
# Step 4: Process .vtk files and generate images for visualisation
#
##################################################################

num_timesteps = 10

start = time.time()
left, right, rgb, depth = generate_images_vtk(sim_id, nprocs, num_timesteps)
end = time.time()
timing['elapsed'].append(end - start)
timing['steps'].append(
    'Step 4: Process .vtk files and generate images for visualisation ')

print("Step 4 completed successfully\n\n")
print("Starting Step 5 (Compute drag)")
print("###################################################################\n")
#
# Step 5: Compute drag from simulation output
#
##################################################################

start = time.time()
drag = computedrag.compute_drag(sim_id, nprocs, num_timesteps)

model.set_drag(sim_id, drag)
end = time.time()
timing['elapsed'].append(end - start)
timing['steps'].append('Step 5: Compute drag from simulation output')

print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")

print("Starting Step 6 (Generate PDF)")
print("###################################################################\n")
#
# Step 6: Generate PDF for printing
#
##################################################################
start = time.time()
images = [
    depth,
    rgb,
    left,
    right,
]

build_sim_document(sim_id, images)
start = time.time()
elapsed_time_file = model.run_directory(sim_id) + '/elapsed.json'
with open(elapsed_time_file, 'w') as outfile:
    json.dump(timing, outfile)
