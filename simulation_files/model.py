
import xml
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import traci
import sys
import subprocess

def genTLSdictionary():
    tls_ids = traci.trafficlight.getIDList()

    tls_cooldown_status = {
    tls_id: {"cooldown": False, "cooldown_time": 0.0, "stolen_tls_phase": None, "originalcyclelength":0.0, "stolen_time":0.0, "benefited_tls_phase": None, "yellow_before_benf_phase": None, "yellow_after" : None, "lenphases" : None} #making a dictionary for each tls
    for tls_id in tls_ids
    }
    return tls_cooldown_status

def getTramList():
    vehList = traci.vehicle.getIDList()
    tramList = list(filter(lambda x: "tram" in x, vehList))# Get all tramss
    return tramList

def getTramInfo(tram):
    tls_info = traci.vehicle.getNextTLS(tram)
    if not tls_info:
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = None, None, None, None
    else:
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = tls_info[0]
    return tlsID, tlsIndex, tram_to_tls_distance, tls_state

def phaseSearch(tram,tlsID):
    tram_lane = traci.vehicle.getLaneID(tram)
    tram_route=traci.vehicle.getRoute(tram)
    current_edge = traci.vehicle.getRouteIndex(tram)
    next_edge = tram_route[current_edge + 1]
    controlled_links = traci.trafficlight.getControlledLinks(tlsID) #getting the lanes that are controlled by the tls
    tram_index = None

    for phase_index, link_pair in enumerate(controlled_links): #finding the correct index for the tram 
        for link in link_pair:
            if tram_lane == link[0] and next_edge in link[1]: #determining 
                tram_index = phase_index
                break
            elif next_edge in link[0]: #this is for the cases when there is a very short edge right in front of the intersection
                next_edge=tram_route[current_edge + 2]
                if next_edge in link[1]:
                    tram_index = phase_index
                    break
    return tram_index

def phaseSearch2(tram_index, tlsID):
    tls_logics = traci.trafficlight.getAllProgramLogics(tlsID) #Here we get the definitions for all of the phases in the TLS program
    tls_logic = tls_logics[0]
    phases = tls_logic.phases
    target_phase = None
    for phase_tls_order, phase in enumerate(phases):
        if phase.state[tram_index] == "u":
            target_phase = phase_tls_order
            break
    return target_phase, phases

def cooldownTurnon(tls_cooldown_status, target_phase, next_phase_index, tlsID, phases):
    stolen_time=traci.trafficlight.getNextSwitch(tlsID) - traci.simulation.getTime() #determine how much time we stole from the phase, from which we switched
    stolen_tls_phase=traci.trafficlight.getPhase(tlsID) #what phase did we steal from
    original_stolen_phase_duration = phases[stolen_tls_phase].duration
    tls_cooldown_status[tlsID]["stolen_tls_phase"]= stolen_tls_phase
    tls_cooldown_status[tlsID]["originalcyclelength"]= original_stolen_phase_duration
    tls_cooldown_status[tlsID]["stolen_time"]= stolen_time
    tls_cooldown_status[tlsID]["yellow_before_benf_phase"]= target_phase
    tls_cooldown_status[tlsID]["benefited_tls_phase"]= next_phase_index
    tls_cooldown_status[tlsID]["cooldown"] = True
    tls_cooldown_status[tlsID]["cooldown_time"]=0.0 ##slight addition so that the skipped phase algorithm works 
    #tls_cooldown_status[tlsID]["cooldown_time"] += -granted_time #this so that the 60 seconds actually cover the next cycle
    tls_cooldown_status[tlsID]["lenphases"]=len(phases)
        
    return tls_cooldown_status

def nextPhase(target_phase, tlsID, phases):
    if target_phase is not None:
        traci.trafficlight.setPhase(tlsID, target_phase)
    else:
        error(tlsID, "is broken")


def tlsStateChange(tram, tls_cooldown_status, tram_to_tls_det_distance, red_min_duration_coefficient, prio_requests, granted_prio, time_list_a, time_list_b, time_list_c):
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = getTramInfo(tram)
        if tlsID and tram_to_tls_distance < tram_to_tls_det_distance: #check if the tram is next to the intersection (1.5 is just a value that worked)
            prio_requests += 1
            if (tls_state not in ["R", "r"]) or tls_cooldown_status[tlsID]["cooldown"] or tlsIndex==tls_cooldown_status[tlsID]["yellow_before_benf_phase"] : #if the phase is yellow before green or green, we pass on to the next tram
                pass
            else:
                red_phase_duration = traci.trafficlight.getPhaseDuration(tlsID)
                red_spent_duration = traci.trafficlight.getSpentDuration(tlsID)
                if red_spent_duration < red_min_duration_coefficient * red_phase_duration:
                    pass
                else:
                    tram_index = phaseSearch(tram, tlsID)
                    target_phase, phases = phaseSearch2(tram_index, tlsID)
                    next_phase_index = (target_phase + 1) % len(phases)
                    tls_cooldown_status =  cooldownTurnon(tls_cooldown_status, target_phase, next_phase_index, tlsID, phases) 
                    nextPhase(target_phase, tlsID, phases)
                    granted_prio += 1
                    if tlsID == "J36":
                        time_list_a.append(traci.simulation.getTime())
                    elif tlsID == "cluster2264846650_2264846651_2264924925_2264924930_#4more":
                        time_list_b.append([traci.simulation.getTime(), tlsID])
                    elif tlsID == "J24":
                        time_list_c.append([traci.simulation.getTime(), tlsID])             
        return tls_cooldown_status, prio_requests, granted_prio, time_list_a, time_list_b, time_list_c

def phaseSkip(tls, tls_id, skipped_phases):
    if traci.trafficlight.getPhase(tls_id) == tls["yellow_before_benf_phase"] and (tls["cooldown_time"]>5 or tls["cooldown"]==False):
                skip_phase=(tls["yellow_before_benf_phase"]+3)%tls["lenphases"]
                traci.trafficlight.setPhase(tls_id, skip_phase)
                tls["yellow_before_benf_phase"]=None 
                skipped_phases += 1
    return tls, skipped_phases
    
def compensation(tls, tls_id, granted_comp): ## Compensating the stolen time, giving it back to the phase from which we stole it
    if traci.trafficlight.getPhase(tls_id)==tls["stolen_tls_phase"]: 
                new_time=tls["originalcyclelength"]+tls["stolen_time"]
                traci.trafficlight.setPhaseDuration(tls_id, new_time)
                tls["originalcyclelength"]=0.0
                tls["stolen_tls_phase"]=None
                granted_comp += 1
    return tls, granted_comp

def cooldownCount(tls, cooldown_time, steptime):
    if tls["cooldown"]:
            tls["cooldown_time"] += steptime
            if tls["cooldown_time"] >= cooldown_time: #turn off the cooldown if the time lapsed is over the defined cooldown time
                tls["cooldown"]=False
                tls["cooldown_time"]=0
    return tls

def cooldownUpdate(tls_cooldown_status, cooldown_time, steptime, skipped_phases, granted_comp, way):
    for tls_id, tls in tls_cooldown_status.items():
        if way=="spc" or way=="spnc":
            tls, skipped_phases = phaseSkip(tls, tls_id, skipped_phases)
        if way=="spc" or way=="nspc":
            tls, granted_comp = compensation(tls, tls_id, granted_comp)
        tls = cooldownCount(tls, cooldown_time, steptime)
    return tls_cooldown_status, skipped_phases, granted_comp

def rename_file(file, namebase):
    os.replace(file,namebase+".xml")

def make_a_df(name, red_min_duration_coefficient, cooldownTime, strategy, mode, skip_phase, compensation, prio_requests, granted_prio, skipped_phases, granted_comp):
    df= pd.read_csv(name + ".csv", delimiter=';', low_memory=False)
    df["minimum_red_coefficient"]= red_min_duration_coefficient
    df["cooldown_duration"]= cooldownTime
    df["strategy"]= strategy
    df["mode"]= mode
    df["skip_phase"]= skip_phase
    df["compensation"]= compensation
    df["priority_requests"]= prio_requests
    df["granted_priority_requests"]= granted_prio
    df["skipped_phases"]= skipped_phases
    df["granted_compensation"]= granted_comp
    os.remove(name + ".csv")
    return df

def file_output(number, xml2csv_path, path_0, list_files):
    for file in list_files:       
        path = f"{path_0}/simulations/run_{number}/{file}_{number}.xml"
        subprocess.run(["python3", xml2csv_path, path])
        os.remove(path)
    


def run_simulation_prio(sumoCmd, simulationTime, tram_to_tls_det_distance, red_min_duration_coefficient, cooldownTime, stepTime, way, time_list_a, time_list_b, time_list_c):
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
        for tram in tramList:
            tls_cooldown_status, prio_requests, granted_prio, time_list_a, time_list_b, time_list_c = tlsStateChange(tram, tls_cooldown_status, tram_to_tls_det_distance, red_min_duration_coefficient, prio_requests, granted_prio, time_list_a, time_list_b, time_list_c)
            tls_cooldown_status, skipped_phases, granted_comp  = cooldownUpdate(tls_cooldown_status, cooldownTime, stepTime, skipped_phases, granted_comp, way)
        step += 1

    traci.close()
    return prio_requests, granted_prio, skipped_phases, granted_comp, time_list_a, time_list_b, time_list_c


def make_a_df_variables(number, red_min_duration_coefficient, cooldownTime, strategy, mode, skip_phase, compensation, prio_requests, granted_prio, skipped_phases, granted_comp, path_0):
    df= pd.DataFrame()
    row = {
        "number": number,
        "minimum_red_coefficient": red_min_duration_coefficient,
        "cooldown_duration": cooldownTime,
        "strategy": strategy,
        "mode": mode,
        "skip_phase": skip_phase,
        "compensation": compensation,
        "priority_requests": prio_requests,
        "granted_priority_requests": granted_prio,
        "skipped_phases": skipped_phases,
        "granted_compensation": granted_comp
    }
    row_df = pd.DataFrame([row])  # row from above
    df = pd.concat([df, row_df], ignore_index=True)
    df.to_csv(f"{path_0}/outputs/run_{number}/variables_{number}.csv", index=False)
    return df


def move_via_os(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        fdst.write(fsrc.read())
    os.remove(src)
