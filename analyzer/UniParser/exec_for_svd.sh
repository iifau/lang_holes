#!/bin/bash
#SBATCH --time=120:00:00

# Executable
source my_env/bin/activate
python for_svd.py