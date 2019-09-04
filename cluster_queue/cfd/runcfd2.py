
import os
from cfdpi_step5 import *
from createcontoureps import *
from computedrag import *


# Default entries
project_name = "square"
nprocs = 1

if len(sys.argv) > 1:
    project_name = sys.argv[1]
if len(sys.argv) > 2:
    nprocs = int(sys.argv[2])

num_timesteps = 100

dst="./" + project_name + "/mesh/"
#dst="./" + project_name
os.chdir(dst)

#step5_generate_vtk_files(project_name, nprocs)
#step6_generate_images_vtk(project_name, nprocs, num_timesteps)
compute_drag(project_name, nprocs, num_timesteps)

print("Step 6 completed successfully\n\n")

print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")


