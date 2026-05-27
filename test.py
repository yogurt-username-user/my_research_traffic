cooldown_list=[5,30,60,90,120]
red_coeff_list=[0.0,0.25,0.5,0.75]
mode_list=["fixed", "actuated"]
ways=["nspc","nspnc"]
time=39600
with open("params.txt", "w") as f:
    f.write(f"--number {1} --cooldown {0} --way {'nopriority'} --red_coeff {0} --mode {'fixed'} --time {time}\n")
    f.write(f"--number {2} --cooldown {0} --way {'nopriority'} --red_coeff {0} --mode {'actuated'} --time {time}\n")
    num = 3
    # Add your first two special combos manually if needed
    for coeff in red_coeff_list:
        for cd in cooldown_list:
            for way in ways:
                for mode in mode_list:
                    f.write(f"--number {num} --cooldown {cd} --way {way} --red_coeff {coeff} --mode {mode} --time {time}\n")
                    num += 1


