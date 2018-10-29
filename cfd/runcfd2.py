
import os
from cfdpi_step5 import *
from cfdpi_step6 import *


if_serial = True

project_name = "test3"

num_timesteps = 10

dst="./" + project_name + "/mesh/"
os.chdir(dst)

#step5_generate_vtk_files(project_name, if_serial)
step6_generate_images_vtk(project_name, if_serial, num_timesteps)

print("Step 6 completed successfully\n\n")

print("Hurrayyyyy! The program is executed successfully.")
print("\nYou can now display the images\n")


