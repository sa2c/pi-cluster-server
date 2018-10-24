
import os


def step5_generate_vtk_files(project_name, if_serial):
    print("step5_generate_vtk_files")

    print("The dir is: %s", os.getcwd())
    os.chdir("mesh")

    #fname_nodes = "./" + project_name + "/mesh/mesh.nodes"
    #fname_elems = "./" + project_name + "/mesh/mesh.elements"
    #fname_field = "./" + project_name + "/mesh/ElmerOutput.ep"

    fname_nodes = "mesh.nodes"
    fname_elems = "mesh.elements"
    fname_field = "ElmerOutput.ep"

    cmd = "../../elmerpostprocessserial " + fname_nodes + " " + fname_elems + " " + fname_field
    os.system(cmd)

    #cmd=""
    #if if_serial == True:
    #cmd = cmd + "./elmerpostprocess  " + step5_input_fname + "  " + str(num_timesteps)
    #else:
    #cmd = cmd + "./elmerpostprocessparallel  " + step5_input_fname + "  " + num_timesteps
    #print(cmd)
    #os.system(cmd)

    return
##################################################
##################################################
