import os
base_path = os.path.dirname(os.path.realpath(__file__))

# Output files
poly_fname = "simulation.poly"

# Configuration files
elmer_sif_file = f"{base_path}/config.sif"

# Executables
triangle_exe = f"{base_path}/triangle-lib/triangle"
elmer_postprocess_serial_exe = f"{base_path}/elmerpostprocessserial"
elmer_postprocess_parallel_exe = f"{base_path}/elmerpostprocessparallel"
