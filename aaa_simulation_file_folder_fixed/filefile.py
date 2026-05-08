import subprocess
import pandas as pd

df_E3=pd.DataFrame()
df_tripinfo=pd.DataFrame()
df_edgedata=pd.DataFrame()
processes=[]
cooldown_list=[5,30,60,90,120]
red_coeff_list=[0,0.25,0.5,0.75]
ways=["spc","nspc","spnc","nspnc"]

combos=[{"num":1, "cd":0, "coeff":0, "way":"no priority" }]

num=2
for coeff in red_coeff_list:
    for cd in cooldown_list:
        for way in ways:
            combo={"num": num, "cd": cd, "coeff": coeff, "way":way}
            combos.appen(combo)
            num += 1

template_path = "DODE_new.add.xml"
with open(template_path, "r") as f:
    template = f.read()

template_path = "DODE.sumocfg"
with open(template_path, "r") as f:
    template2 = f.read()

for c in combos:
    # Build the base command
    n=c["num"]
    output = template.replace("{number}", str(n))
    with open(f"DODE_new{c["num"]}.add.xml", "w") as out:
        out.write(output)
    output = template2.replace("{number}", str(n))
    with open(f"DODE_{c["num"]}.sumocfg", "w") as out:
        out.write(output)
    cmd = [
        "python3", "main_1.py", 
        "--number", str(c["num"]), 
        "--cooldown", str(c["cd"]), 
        "--way", str(c["way"]),
        "--red_coeff"
    ]
    
    # Add all coefficients from the list to the command
    for val in c["coeff"]:
        cmd.append(str(val))

    # Launch process
    p = subprocess.Popen(cmd)
    processes.append(p)

for p in processes:
    p.wait()

print("All processes have finished.")

for i in range(num):
    df = pd.read_csv(f"E3_output_{i}.csv")
    df_E3 = pd.concat([df_E3, df], ignore_index=True)
    df_E3.to_csv("DODE_E3_output_fixed.csv")
    df = pd.read_csv(f"tripinfo_{i}.csv")
    df_tripinfo = pd.concat([df_tripinfo, df], ignore_index=True)
    df_tripinfo.to_csv("tripinfo_fixed.csv")
    df = pd.read_csv(f"edgedata_{i}.csv")
    df_edgedata = pd.concat([df_edgedata, df], ignore_index=True)
    df_edgedata.to_csv("edgedata_fixed.csv")
