This folder contains files to run the simulations from -insert project name-.
## Structure
The simulation_files folder contains the files needed to execute the script, templates for the sumo configuration file and additional file, and the network files (actuated and fixed traffic signal plans). ```main_1.py``` is the script that executes the simulation run. In ```model.py``` functions are defined which are used in the ```main_1.py``` file. ```config.py``` contains variables used for the simulation run, which can be adjusted if needed. 

To run the simulation following variables have to be given by user:
- ```number```: (int) A symbolic number used to differentiate between outputs of multiple runs
- ```cooldownTime```: (float) Reserved time after granted priority when no priority can be granted
- ```red_min_duration_coefficient```: (float) Minimum passed phased duration before priority can be granted
- ```way```: (str) Compensation or priority strategy, following 5 options are available
  - ```spc```: Skipping benefitted phase in the following cycle and compensating the disadvantaged phase with stolen time
  - ```nspc```: Only compensating the disadvantaged phase with stolen time
  - ```spnc```: Only skipping benefitted phase in the following cycle
  - ```nspnc```: No compensation or skipping
  - ```nopriority```: No priority for trams (base case)
- ```mode```: (str) traffic signal plan, either ```fixed``` or ```actuated```
- ```simulationTime```: (float) Time until which to run the simulation (full simulation ends at 39600)

Three options for running are available:
1. Running locally via an IDE
2. Running locally via terminal command
3. Running a container

## 1. Running via an IDE
Download the repository onto your device. To successfully run it make sure your ```$SUMO_HOME``` is set up correctly. In the ```config.py``` file define path to sumo under ```sumoBinary``` variable and define the simulation variables ```number```,```red_min_duration_coefficient```,```way```,```mode```,```simulationTime```.
Execute ```main_1.py``` via the IDE user interface.

## 2. Running locally via terminal command
Download the repository onto your device. Run via terminal with ```python /your/path/to/repo/folder/simulation_files/main_1.py --number {} --cooldown {} --way {} --red_coeff {} --mode {} --time {}```, after replacing the path to ```main_1.py``` file and replacing the brackets for your simulation variables
