seed_list=[23423, 23424, 23425, 23426, 23427]
cooldown_list=[5,30,60,90,120]
red_coeff_list=[0.0,0.25,0.5,0.75]
mode_list=["fixed", "actuated"]
ways=["nspc","nspnc"]
time=39600
num=1
with open("params.txt", "w") as f:
    for seed in seed_list:
        f.write(f"--number {num} --cooldown {0.0} --way {'nopriority'} --red_coeff {0.0} --mode {'fixed'} --time {time} --seed {seed}\n")
        num=num+1
        f.write(f"--number {num} --cooldown {0.0} --way {'nopriority'} --red_coeff {0.0} --mode {'actuated'} --time {time} --seed {seed}\n")
        num=num+1
        # Add your first two special combos manually if needed
        for coeff in red_coeff_list:
            for cd in cooldown_list:
                for way in ways:
                    for mode in mode_list:
                        f.write(f"--number {num} --cooldown {cd} --way {way} --red_coeff {coeff} --mode {mode} --time {time} --seed {seed}\n")
                        num += 1


