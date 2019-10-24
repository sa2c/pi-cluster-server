import model
import settings
import os


def generate_vtk_files(sim_id, nprocs):
    print("generate_vtk_files")

    project_dir = model.run_directory(sim_id)

    if (nprocs == 1):
        fname_nodes = "simulation/mesh.nodes"
        fname_elems = "simulation/mesh.elements"
        fname_field = "simulation/ElmerOutput.ep"

        cmd = settings.elmer_postprocess_serial_exe + " " + fname_nodes + " " + fname_elems + " " + fname_field
    else:
        fname_elems = "simulation/partitioning." + str(nprocs) + "/part"
        fname_field = "simulation/ElmerOutput"
        cmd = 'cd {project_dir} && '.format(project_dir=project_dir) + \
              settings.elmer_postprocess_parallel_exe + \
              " " + fname_elems + " " + fname_field + " " + str(nprocs)
    print("Running: " + cmd)

    exit_code = os.system(cmd)

    if exit_code != 0:
        print("Error running Elmer command :\n {cmd}".format(cmd=cmd))
        exit(1)
    return


##################################################
##################################################
