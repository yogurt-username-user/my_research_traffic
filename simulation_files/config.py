import os
import sys


startTime = 21600 #time at which the simulation starts
stepTime = 0.25 #length of the step 0.25
tram_to_tls_det_distance = 1.5 #distance away from tls, where trams get detected
list_files=["tripinfo", "edgedata", "a_tls_states", "b_tls_states", "c_tls_states"]



# Sumo binary and path
sumoBinary = "sumo-gui" 


# Simulation variables
number = 2
cooldownTime = 30
red_min_duration_coefficient = 0
way = "nspc"
mode="fixed"
simulationTime = 31600
seed=23435 #23423, 23424, ....5, ....6, ....7
