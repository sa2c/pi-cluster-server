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
from cfdpi_step3 import *
from cfdpi_step4 import *
from cfdpi_step5 import *
#from cfdpi_step6 import *
from createcontoureps import *



# Read the project name and other flags from the command line arguments
#

# Default entries
project_name = "Square"
nprocs = 1
hostfile = "hostfile1"
diskaddress = "127.0.0.1:"+os.getcwd()+"/"

if len(sys.argv) > 1:
    project_name = sys.argv[1]

if len(sys.argv) > 2:
    nprocs = int(sys.argv[2])

if len(sys.argv) > 3:
    hostfile = sys.argv[3]

if len(sys.argv) > 4:
    diskaddress = sys.argv[4]


# Check if a directory with the given project name exists,
# And delete it, if it exists
#
if os.path.exists(project_name):
    cmd="rm -rf " + project_name
    os.system(cmd)

# Create a directory with the project_name
#
cmd="mkdir " + project_name
os.system(cmd)


print("Starting Step 1 (Knect  -->  Depth Map)")
print("###################################################################\n")
#
# Step 1: Generate the depth map from Knect output
#
###################################################



print("Step 1 completed successfully\n\n")
print("Starting Step 2 (Depth Map  -->  Model Outline)")
print("###################################################################\n")
#
# Step 2: Generate the outline of the model from the depth map
#
##############################################################



print("Step 2 completed successfully\n\n")
print("Starting Step 3 (Model Outline  -->  CFD Mesh)")
print("###################################################################\n")
#
# Step 3: Read the outline and generate the mesh
#
#################################################


step3_generate_mesh_from_outline(project_name, nprocs)


print("Step 3 completed successfully\n\n")
print("Starting Step 4 (CFD Mesh  -->  CFD Results)")
print("###################################################################\n")
#
# Step 4: Run Elmer with the mesh file generated in Step 1
#
##########################################################

step4_run_cfd_simulation(project_name, hostfile, nprocs, diskaddress)



print("Step 4 completed successfully\n\n")
print("Starting Step 5 (CFD Results  -->  VTK files)")
print("###################################################################\n")
#
# Step 3: Create .vtk files from Elmer output
#
#####################################################

step5_generate_vtk_files(project_name, nprocs)


print("Step 5 completed successfully\n\n")
print("Starting Step 6 (VTK files  -->  Images)")
print("###################################################################\n")
#
# Step 6: Process .vtk files and generate images for visualisation
#
##################################################################

num_timesteps = 10

step6_generate_images_vtk(project_name, nprocs, num_timesteps)


print("Step 6 completed successfully\n\n")

print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")


