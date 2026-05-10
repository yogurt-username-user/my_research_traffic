import os
import sys
import xml
import subprocess
import pandas as pd 
from config import simulationTime, startTime, stepTime, tram_to_tls_det_distance, sumoBinary, xml2csv_path
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--number", type=int)
parser.add_argument("--cooldown", type=float, nargs='+') 
parser.add_argument("--red_coeff", type=float, nargs='+') 
parser.add_argument("--way", type=str, nargs='+') 
parser.add_argument("--mode", type=str, nargs='+')
args = parser.parse_args()

number = args.number
cooldownTime_list = args.cooldown
red_min_duration_coefficient_list = args.red_coeff
way = args.way
mode= str(args.mode)
mode=mode[2:-2]

template_path = "DODE_new.add.xml"
with open(template_path, "r") as f:
    template = f.read()
template_path = "DODE.sumocfg"
with open(template_path, "r") as f:
    template2 = f.read()

output = template.replace("{number}", str(number))
with open(f"DODE_new{number}.add.xml", "w") as out:
    out.write(output)
output = template2.replace("{number}", str(number))
output = output.replace("{mode}", mode)
with open(f"DODE_{number}.sumocfg", "w") as out:
    out.write(output)


strategy = "pt_priority"
df_E3_final = pd.DataFrame()
df_tripinfo_final = pd.DataFrame()
df_edgedata_final = pd.DataFrame()


os.environ['SUMO_HOME'] = "/usr/share/sumo"
sumo_config_path = f"DODE_{number}.sumocfg" 
sumoCmd = [sumoBinary, "-c", sumo_config_path, "--start", "--quit-on-end"]
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

if not os.path.exists(sumo_config_path):
    sys.exit(f"Error: Config file not found at {sumo_config_path}")


import traci
from model import *
if way != "no priority":
    for cooldownTime in cooldownTime_list:
        for red_min_duration_coefficient in red_min_duration_coefficient_list:
            ## Skip phase + compensation case
            nfd_name_file_output, trips_name_file_output, edgedata_name_file_output = file_names_def(way)

            #Running the siimulation
            prio_requests, granted_prio, skipped_phases, granted_comp = run_simulation_prio(sumoCmd, simulationTime, tram_to_tls_det_distance, red_min_duration_coefficient, cooldownTime, stepTime, way)
            
            #Renaming the files 
            str1 = str(cooldownTime)
            str2 = str(red_min_duration_coefficient)

            nfd_name, trips_name, edgedata_name = file_output(nfd_name_file_output, trips_name_file_output, edgedata_name_file_output, str1, str2, mode, number, xml2csv_path)

            df_E3_spc = make_a_df(nfd_name, red_min_duration_coefficient, cooldownTime, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
            df_tripinfo_spc = make_a_df(trips_name, red_min_duration_coefficient, cooldownTime, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
            df_edgedata_spc = make_a_df(edgedata_name, red_min_duration_coefficient, cooldownTime, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
            
            df_E3_final = pd.concat([df_E3_final, df_E3_spc], ignore_index=True)
            df_tripinfo_final = pd.concat([df_tripinfo_final, df_tripinfo_spc], ignore_index=True)
            df_edgedata_final = pd.concat([df_edgedata_final, df_edgedata_spc], ignore_index=True)


else:
    strategy = "pt"

    nfd_name_file_output= "DODE_E3_output_pt" 
    trips_name_file_output= "tripinfo_pt"
    edgedata_name_file_output="spc_edgedata_pt"

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

    nfd_name, trips_name, edgedata_name = file_output(nfd_name_file_output, trips_name_file_output, edgedata_name_file_output, str1, str2, mode, number, xml2csv_path)

    df_E3_spc = make_a_df(nfd_name, None, None, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
    df_tripinfo_spc = make_a_df(trips_name, None, None, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
    df_edgedata_spc = make_a_df(edgedata_name, None, None, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)

df_E3_final = pd.concat([df_E3_final, df_E3_spc], ignore_index=True)
df_tripinfo_final = pd.concat([df_tripinfo_final, df_tripinfo_spc], ignore_index=True)
df_edgedata_final = pd.concat([df_edgedata_final, df_edgedata_spc], ignore_index=True)


df_E3_final.to_csv(f"E3_output_{number}.csv", index=False)
df_tripinfo_final.to_csv(f"tripinfo_{number}.csv", index=False)
df_edgedata_final.to_csv(f"edgedata_{number}.csv", index=False)





