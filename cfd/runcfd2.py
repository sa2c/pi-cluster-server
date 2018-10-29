
import os
from cfdpi_step5 import *
from createcontoureps import *


# Default entries
project_name = "square"
if_serial = True

if len(sys.argv) > 1:
    project_name = sys.argv[1]

if_serial = True

num_timesteps = 100

dst="./" + project_name + "/mesh/"
os.chdir(dst)

#step5_generate_vtk_files(project_name, if_serial)
step6_generate_images_vtk(project_name, if_serial, num_timesteps)

print("Step 6 completed successfully\n\n")

print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")


