import os
import sys
import xml
import subprocess
import pandas as pd 
from config import simulationTime, startTime, stepTime, tram_to_tls_det_distance, sumoBinary, number, cooldownTime, red_min_duration_coefficient, way, simulationTime, mode, list_files
import argparse




# Argument parser for inputs!
parser = argparse.ArgumentParser()
parser.add_argument("--number", type=int)
parser.add_argument("--cooldown", type=float) 
parser.add_argument("--red_coeff", type=float) 
parser.add_argument("--way", type=str) 
parser.add_argument("--mode", type=str)
parser.add_argument("--time", type=float)
args = parser.parse_args()

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_path)
parent=os.path.join(script_path, os.pardir)

path_0 = os.path.abspath(parent)
os.chdir(path_0)


if all(list(args.__dict__.values())):
    number = args.number
    cooldownTime = args.cooldown
    red_min_duration_coefficient = args.red_coeff
    way = args.way
    simulationTime=args.time
    mode= str(args.mode)
else:
    message=f"------------\nRunning simulation with variables from config file:\n Number: {number}\n Minimum phase duration coefficient:{red_min_duration_coefficient}\n Cooldown duration: {cooldownTime}\n Mode: {mode} \n Strategy: {way}\n-------------"
    print(message)

if not os.path.isdir(f"{path_0}/simulations/run_{number}"):
    os.makedirs(f"{path_0}/simulations/run_{number}")

if not os.path.isdir(f"{path_0}/outputs/run_{number}"):
    os.makedirs(f"{path_0}/outputs/run_{number}")

template_path = f"{path_0}/simulation_files/DODE_new.add.xml"

with open(template_path, "r") as f:
    template_add = f.read()
template_path = f"{path_0}/simulation_files/DODE.sumocfg"
with open(template_path, "r") as f:
    template_cfg = f.read()

output = template_add.replace("{number}", str(number))
with open(f"{path_0}/simulations/run_{number}/DODE_new{number}.add.xml", "w") as out:
    out.write(output)

output = template_cfg.replace("{number}", str(number))
output = output.replace("{mode}", mode)
output = output.replace("{path}",path_0)
with open(f"{path_0}/simulations/run_{number}/DODE_{number}.sumocfg", "w") as out:
    out.write(output)




sumo_config_path = f"{path_0}/simulations/run_{number}/DODE_{number}.sumocfg"
sumoCmd = [sumoBinary, "-c", sumo_config_path, "--start", "--quit-on-end"]

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
    from sumolib import checkBinary
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

if not os.path.exists(sumo_config_path):
    sys.exit(f"Error: Config file not found at {sumo_config_path}")
    
xml2csv_path=os.path.join(os.environ['SUMO_HOME'], "tools/xml/xml2csv.py")

import traci
from model import *

if way != "nopriority":
    strategy = "pt_priority"

    time_list_a=[]
    time_list_b=[]
    time_list_c=[]

    prio_requests, granted_prio, skipped_phases, granted_comp, time_list_a, time_list_b, time_list_c = run_simulation_prio(sumoCmd, simulationTime, tram_to_tls_det_distance, red_min_duration_coefficient, cooldownTime, stepTime, way, time_list_a, time_list_b, time_list_c)
    
    #Renaming the files 
    str1 = str(cooldownTime)
    str2 = str(red_min_duration_coefficient)

    file_output(number, xml2csv_path, path_0, list_files)
    
    if way=="spc" or "spnc":
        sp = True
    else:
        sp = False

    if way=="spc" or "nspc":
        co = True
    else:
        co = False

    df_coefficients = make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, sp, co, prio_requests, granted_prio, skipped_phases, granted_comp, path_0)
   
    np.savetxt(f"tls_request_times_a_{number}.csv", time_list_a, delimiter=",", fmt='%s')
    move_via_os(f"tls_request_times_a_{number}.csv", f"{path_0}/outputs/run_{number}/tls_request_times_a_{number}.csv")

    np.savetxt(f"tls_request_times_b_{number}.csv", time_list_b, delimiter=",", fmt='%s')
    move_via_os(f"tls_request_times_b_{number}.csv",  f"{path_0}/outputs/run_{number}/tls_request_times_b_{number}.csv")

    np.savetxt(f"tls_request_times_c_{number}.csv", time_list_c, delimiter=",", fmt='%s')
    move_via_os(f"tls_request_times_c_{number}.csv", f"{path_0}/outputs/run_{number}/tls_request_times_c_{number}.csv")

            


else:
    strategy = "pt"

    traci.start(sumoCmd)

    step = 0
    prio_requests = 0
    granted_prio = 0
    skipped_phases = 0
    granted_comp = 0

    tls_cooldown_status = genTLSdictionary()

    while traci.simulation.getTime() < simulationTime:
        traci.simulationStep()
        tramList = getTramList()
        step += 1
    traci.close()

    #Renaming the files 
    str1 = str(0)
    str2 = str(0)

    file_output(number, xml2csv_path, path_0, list_files)
    df_coefficients = make_a_df_variables(number, None, None, strategy, mode, None, None, prio_requests, granted_prio, skipped_phases, granted_comp, path_0)

# Moving files to the output folder
for file in list_files:
    path_from = f"{path_0}/simulations/run_{number}/{file}_{number}.csv"
    path_to = f"{path_0}/outputs/run_{number}/{file}_{number}.csv"
    move_via_os(path_from, path_to)

move_via_os(f"{path_0}/simulations/run_{number}/edgedata_edge_{number}.xml", f"{path_0}/outputs/run_{number}/edgedata_edge_{number}.xml")






