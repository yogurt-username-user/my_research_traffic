import os
import subprocess

# 1. THE EXPLICIT PATHS
# Path to the tool
xml2csv_path = "/Library/Frameworks/EclipseSUMO.framework/Versions/1.25.0/EclipseSUMO/share/sumo/tools/xml/xml2csv.py"
# Path to the libraries (one folder up from 'xml')
sumo_tools_dir = "/Library/Frameworks/EclipseSUMO.framework/Versions/1.25.0/EclipseSUMO/share/sumo/tools"

# 2. FILE NAMES
nfd_base = "nspncf_DODE_E3_output_pt_priority" 
trips_base = "nspncf_tripinfo_pt_priority"
edgedata_base = "nspncf_edgedata_pt_priority"

cooldowns = [5, 30, 60, 90, 120]
red_coeffs = [0, 0.3, 0.5]

# 3. SET THE ENVIRONMENT
# This tells the subprocess where to find 'sumolib'
env = os.environ.copy()
env["PYTHONPATH"] = sumo_tools_dir + ":" + env.get("PYTHONPATH", "")

for c in cooldowns:
    for r in red_coeffs:
        suffix = f"_{c}_{r}.xml"
        files_to_convert = [
            nfd_base + suffix,
            trips_base + suffix,
            edgedata_base + suffix
        ]
        
        print(f"--- Converting set for {c}, {r} ---")
        
        for file_name in files_to_convert:
            if os.path.exists(file_name):
                # Pass the 'env' to the subprocess
                result = subprocess.run(["python3", xml2csv_path, file_name], env=env)
                
                if result.returncode == 0:
                    print(f"Success: {file_name}")
                else:
                    print(f"Failed: {file_name}")
            else:
                print(f"Skipping: {file_name} (File not found)")

print("Done.")