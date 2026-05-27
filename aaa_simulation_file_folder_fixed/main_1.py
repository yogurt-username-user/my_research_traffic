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
parser.add_argument("--way", type=str) 
parser.add_argument("--mode", type=str)
parser.add_argument("--time", type=float)
args = parser.parse_args()

number = args.number
cooldownTime_list = args.cooldown
red_min_duration_coefficient_list = args.red_coeff
way = args.way
simulationTime=args.time
mode= str(args.mode)


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

nfd_name_file_output= "E3_output"
trips_name_file_output= "tripinfo"
edgedata_name_file_output= "edgedata"
tls_state_file_output="tls_states"
import traci
from model import *
if way != "nopriority":
    time_list_a=[]
    time_list_b=[]
    time_list_c=[]
    for cooldownTime in cooldownTime_list:
        for red_min_duration_coefficient in red_min_duration_coefficient_list:
            ## Skip phase + compensation case
            

            #Running the siimulation
            prio_requests, granted_prio, skipped_phases, granted_comp, time_list_a, time_list_b, time_list_c = run_simulation_prio(sumoCmd, simulationTime, tram_to_tls_det_distance, red_min_duration_coefficient, cooldownTime, stepTime, way, time_list_a, time_list_b, time_list_c)
            
            #Renaming the files 
            str1 = str(cooldownTime)
            str2 = str(red_min_duration_coefficient)

            nfd_name, trips_name, edgedata_name, tls_state_name = file_output(nfd_name_file_output, trips_name_file_output, edgedata_name_file_output, tls_state_file_output, str1, str2, mode, number, xml2csv_path)

            
            if way=="spc":
                df_coefficients = make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, True, True, prio_requests, granted_prio, skipped_phases, granted_comp)
            elif way=="spnc":
               df_coefficients = make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, True, False, prio_requests, granted_prio, skipped_phases, granted_comp)
            elif way=="nspc":
                df_coefficients = make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, False, True, prio_requests, granted_prio, skipped_phases, granted_comp)
            elif way=="nspnc":
                df_coefficients = make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, False, False, prio_requests, granted_prio, skipped_phases, granted_comp)

            np.savetxt(f"tls_request_times_a_{number}.csv", time_list_a, delimiter=",", fmt='%s')
            move_via_os(f"tls_request_times_a_{number}.csv", "outputs/" + f"tls_request_times_a_{number}.csv")

            np.savetxt(f"tls_request_times_b_{number}.csv", time_list_b, delimiter=",", fmt='%s')
            move_via_os(f"tls_request_times_b_{number}.csv", "outputs/" + f"tls_request_times_b_{number}.csv")

            np.savetxt(f"tls_request_times_c_{number}.csv", time_list_c, delimiter=",", fmt='%s')
            move_via_os(f"tls_request_times_c_{number}.csv", "outputs/" + f"tls_request_times_c_{number}.csv")

            


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

    nfd_name, trips_name, edgedata_name, tls_state_name = file_output(nfd_name_file_output, trips_name_file_output, edgedata_name_file_output, tls_state_file_output, str1, str2, mode, number, xml2csv_path)
    df_coefficients = make_a_df_variables(number, None, None, strategy, mode, None, None, prio_requests, granted_prio, skipped_phases, granted_comp)


move_via_os(nfd_name + ".csv", "outputs/" + nfd_name + ".csv")
move_via_os(trips_name + ".csv", "outputs/" + trips_name + ".csv")
move_via_os(edgedata_name + ".csv", "outputs/" + edgedata_name + ".csv")

move_via_os("a_" + tls_state_name + ".csv", "outputs/" + "a_" + tls_state_name + ".csv")
move_via_os("b_" + tls_state_name + ".csv", "outputs/" + "b_" + tls_state_name + ".csv")
move_via_os("c_" + tls_state_name + ".csv", "outputs/" + "c_" + tls_state_name + ".csv")







