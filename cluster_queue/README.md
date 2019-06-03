
# The Cluster Queue

The queue handles incoming simulations jobs on the 


## Installation

First install the required python modules
```
pip install -r requirements.txt
```
This enables running tests during rest of the installation process.

If you would rather not touch your python environment, use the Pipenv virtual environment instead
```
pipenv install
pipenv shell
```

There are two c++ files in the cfd folder. Compile these
```
cd cfd
g++ -o elmerpostprocessserial elmerpostprocessserial.cpp
g++ -o elmerpostprocessparallel elmerpostprocessparallel.cpp
```
The cfd folder also contains the triangle-lib.
Compile that on as well
```
cd triangle-lib
make
cd ..
```

### Installing Elmer

We use [Elmer](https://www.csc.fi/web/elmer) for the actual computation.
This requires that Elmer is installed and the ```ElmerGrid```,
```ElmerSolver``` and ```ElmerSolver_mpi``` executables are found in PATH.
On Ubuntu you can simply use the PPA provided by CSC,
```
$ sudo apt-add-repository ppa:elmer-csc-ubuntu/elmer-csc-ppa
$ sudo apt-get update
$ sudo apt-get install elmerfem-csc
```

On a Rapberry Pi, you have need to compile in manually. First download and
install the [metis](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview) and [parmetis](http://glaros.dtc.umn.edu/gkhome/metis/parmetis/overview) libraries
```
$wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
$tar -xvgf metis-5.1.0.tar.gz
$cd metis-5.1.0
$make config
$make
$sudo make install
```
```
$wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/parmetis/parmetis-4.0.3.tar.gz
$tar -xvgf parmetis-4.0.3.tar.gz
$cd parmetis-4.0.3
$make config
$make
$sudo make install
```

Once you have these two libraries, create a
directory for Elmer and clone the repository
```
mkdir Elmer
cd Elmer
git clone https://github.com/elmercsc/elmerfem
```
The most recent version of Elmer has a bug that causes a 
segfault on the Pi.
**Checkout version 8.3 before compiling.**
```
git checkout release-8.3
```

Create a build directory and initialise cmake
```
cd .. 
mkdir build
cd build
cmake ../elmerfem
```
The setup is easiest using the ccmake UI,
```
ccmake .
```
Make sure that MPI and Mumps are enabled.
You might also want to disable ELMERGUI to speed up the compilations,
which does take a while.

Compile and install with
```
make
sudo make install
```


### Testing the Installation

Now everything should be ready to run Elmer and the queue.
Test your installation by running
```
python runcfd.py test_contour 4 hostfile_local
```
Keep an eye on any error messages from Elmer.


### Setup

Everything you need to change should be in the settings.py.
Modify the following variables to match your system:

| Variable | |
|-------------|------------------------------|
| diskaddress | Network address to the disk the compute nodes have access to. If the master node and the compute nodes share the disk, just leave this as it is. |
| IPs | A list of the IP addresses of the nodes available to the queue. |
| nnodes | The total number of nodes on the cluster. |
| nslots | The number of (virtual) cores on each node. |
| nodes_per_jobs | The number of nodes that will be reserved for each job. Note that nodes_per_jobs*nslots needs to be the square of an integer. |

