
import os


def generate_vtk_files(project_name, nprocs):
    print("step5_generate_vtk_files")

    print("The dir is: %s", os.getcwd())

    os.chdir("mesh")

    #fname_nodes = "./" + project_name + "/mesh/mesh.nodes"
    #fname_elems = "./" + project_name + "/mesh/mesh.elements"
    #fname_field = "./" + project_name + "/mesh/ElmerOutput.ep"

    if(nprocs == 1):
      fname_nodes = "mesh.nodes"
      fname_elems = "mesh.elements"
      fname_field = "ElmerOutput.ep"

      cmd = "../../elmerpostprocessserial " + fname_nodes + " " + fname_elems + " " + fname_field
    else:
      fname_elems = "./partitioning." + str(nprocs) + "/part"
      fname_field = "ElmerOutput"
      cmd = "../../elmerpostprocessparallel " + fname_elems + " " + fname_field + " " + str(nprocs)

    os.system(cmd)

    return
##################################################
##################################################
