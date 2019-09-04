
import os
import time

def run_cfd_simulation(project_name, hostfile, nprocs, diskaddress):
    print("run_cfd_simulation")

    project_dir="./" + project_name + "/"

    # create the ELMERSOLVER_STARTINFO file
    #
    #######################################
    #os.chdir(project_dir)

    file = open("ELMERSOLVER_STARTINFO", "w") 

    sif_fname = project_name + ".sif"

    file.write(sif_fname) 
    file.write("\n1") 
    file.close()

    # copy the .sif file
    #######################################

    cmd="cp ../test.sif " + sif_fname
    os.system(cmd)

    # run the simulation with Elmer solver
    #######################################

    if(nprocs == 1):
      cmd="ElmerSolver"
      os.system(cmd)
    else:
      # First copy the mesh files over
      cmd="scp -r ../"+project_name+" "+diskaddress+'/cfd'
      os.system(cmd)
      cmd="mpirun --hostfile ../"+hostfile+" -np "+ str(nprocs) + " ElmerSolver_mpi"
      os.system(cmd)
      time.sleep(2)
      cmd="scp -r "+diskaddress+"/cfd/"+project_name+"/* ./"
      os.system(cmd)


    return
##################################################
##################################################

