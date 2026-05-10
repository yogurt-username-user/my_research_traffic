import subprocess
import pandas as pd
import os

df_E3=pd.DataFrame()
df_tripinfo=pd.DataFrame()
df_edgedata=pd.DataFrame()
processes=[]

sim_folder = "aaa_simulation_file_folder_fixed"
sim_dir_abs = os.path.abspath(sim_folder)

cooldown_list=[5,30,60,90,120]
red_coeff_list=[0.0,0.25,0.5,0.75]
mode_list=["fixed", "actuated"]
ways=["spc","nspc","spnc","nspnc"]

combos=[{"num":1, "cd":0, "coeff":0.0, "way":"no priority", "mode":"fixed"}, 
        {"num":2, "cd":0, "coeff":0.0, "way":"no priority", "mode":"actuated"}]

num=3
for coeff in red_coeff_list:
    for cd in cooldown_list:
        for way in ways:
            for mode in mode_list:
                combo={"num": num, "cd": cd, "coeff": coeff, "way":way, "mode":mode}
                combos.append(combo)
                num += 1
print(combos)

for c in combos:
    cmd = [
        "python3", "main_1.py", 
        "--number", str(c["num"]), 
        "--cooldown", str(c["cd"]), 
        "--way", str(c["way"]),
        "--red_coeff", str(c["coeff"]),
        "--mode", str(c["mode"])
    ]
    
    # Launch process
    p = subprocess.Popen(cmd, cwd=sim_dir_abs)
    processes.append(p)

for p in processes:
    p.wait()

print("All processes have finished.")

for j in range(num-1):
    i=j+1
    df = pd.read_csv(f"aaa_simulation_file_folder_fixed/DODE_E3_output_{i}.csv")
    df_E3 = pd.concat([df_E3, df], ignore_index=True)
    df_E3.to_csv("DODE_E3_output.csv")
    df = pd.read_csv(f"aaa_simulation_file_folder_fixed/tripinfo_{i}.csv")
    df_tripinfo = pd.concat([df_tripinfo, df], ignore_index=True)
    df_tripinfo.to_csv("tripinfo.csv")
    df = pd.read_csv(f"aaa_simulation_file_folder_fixed/edgedata_{i}.csv")
    df_edgedata = pd.concat([df_edgedata, df], ignore_index=True)
    df_edgedata.to_csv("edgedata.csv")

# ## Actuated cases
# df_E3=pd.DataFrame()
# df_tripinfo=pd.DataFrame()
# df_edgedata=pd.DataFrame()
# processes=[]
# sim_folder = "aaa_simulation_file_folder_actuated"
# sim_dir_abs = os.path.abspath(sim_folder)

# combos = [
#     {"num": 1, "cd": 5, "coeff": [0.0]},
#     {"num": 2, "cd": 30, "coeff": [0.0]},
#     {"num": 3, "cd": 60, "coeff": [0.0]},
#     {"num": 4, "cd": 90, "coeff": [0.0]},
#     {"num": 5, "cd": 120, "coeff": [0.0]},
#     {"num": 6, "cd": 5, "coeff": [0.25]},
#     {"num": 7, "cd": 30, "coeff": [0.25]},
#     {"num": 8, "cd": 60, "coeff": [0.25]},
#     {"num": 9, "cd": 90, "coeff": [0.25]},
#     {"num": 10, "cd": 120, "coeff": [0.25]},
#     {"num": 11, "cd": 5, "coeff": [0.5,0.75]},
#     {"num": 12, "cd": 30, "coeff": [0.5,0.75]},
#     {"num": 13, "cd": 60, "coeff": [0.5,0.75]},
#     {"num": 14, "cd": 90, "coeff": [0.5,0.75]},
#     {"num": 15, "cd": 120, "coeff": [0.5,0.75]},
# ]

# for c in combos:
#     # Build the base command
#     cmd = [
#         "python3", "main_1.py", 
#         "--number", str(c["num"]), 
#         "--cooldown", str(c["cd"]), 
#         "--red_coeff"
#     ]
    
#     # Add all coefficients from the list to the command
#     for val in c["coeff"]:
#         cmd.append(str(val))

#     # Launch process
#     p = subprocess.Popen(cmd, cwd=sim_dir_abs)
#     processes.append(p)

# for p in processes:
#     p.wait()

# print("All processes have finished. For actuated schedule cases.")

# for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
#     df = pd.read_csv(f"aaa_simulation_file_folder_actuated/E3_output_{i}.csv")
#     df_E3 = pd.concat([df_E3, df], ignore_index=True)
#     df_E3.to_csv("DODE_E3_output_actuated.csv")
#     df = pd.read_csv(f"aaa_simulation_file_folder_actuated/tripinfo_{i}.csv")
#     df_tripinfo = pd.concat([df_tripinfo, df], ignore_index=True)
#     df_tripinfo.to_csv("tripinfo_actuated.csv")
#     df = pd.read_csv(f"aaa_simulation_file_folder_actuated/edgedata_{i}.csv")
#     df_edgedata = pd.concat([df_edgedata, df], ignore_index=True)
#     df_edgedata.to_csv("edgedata_actuated.csv")