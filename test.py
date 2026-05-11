cooldown_list=[5,30,60,90,120]
red_coeff_list=[0.0,0.25,0.5,0.75]
mode_list=["fixed", "actuated"]
ways=["spc","nspc","spnc","nspnc"]

with open("params.txt", "w") as f:
    f.write(f"--number {1} --cooldown {0} --way {'no priority'} --red_coeff {0.0} --mode {'fixed'}\n")
    f.write(f"--number {2} --cooldown {0} --way {'no priority'} --red_coeff {0.0} --mode {'actuated'}\n")
    num = 3
    # Add your first two special combos manually if needed
    for coeff in red_coeff_list:
        for cd in cooldown_list:
            for way in ways:
                for mode in mode_list:
                    f.write(f"--number {num} --cooldown {cd} --way {way} --red_coeff {coeff} --mode {mode}\n")
                    num += 1


#!/bin/bash
#SBATCH --job-name=sumo_sim
#SBATCH --output=logs/sim_%a.out
#SBATCH --error=logs/sim_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=01:00:00
#SBATCH --array=1-162  # Adjust this based on how many combos you have

# 1. Load the module
module load apptainer


PARAMS=$(sed -n "${SLURM_ARRAY_TASK_ID}p" params.txt)


apptainer run sumo-sim.sif $PARAMS