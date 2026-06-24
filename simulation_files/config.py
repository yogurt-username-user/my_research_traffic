import os
import sys


startTime = 21600 #time at which the simulation starts
stepTime = 0.25 #length of the step 0.25
tram_to_tls_det_distance = 1.5 #distance away from tls, where trams get detected
list_files=["E3_output", "tripinfo", "edgedata", "a_tls_states", "b_tls_states", "c_tls_states"]


# Sumo binary and path
sumoBinary = "sumo" 

# Simulation variables
number = 2
cooldownTime = 30
red_min_duration_coefficient = 0
way = "nspc"
mode="fixed"
simulationTime = 22000

