import subprocess
import pandas as pd
df_E3=pd.DataFrame()
df_tripinfo=pd.DataFrame()
df_edgedata=pd.DataFrame()
for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
    df = pd.read_csv(f"E3_output_{i}.csv")
    df_E3 = pd.concat([df_E3, df], ignore_index=True)
    df_E3.to_csv("DODE_E3_output_fixed.csv")
    df = pd.read_csv(f"tripinfo_{i}.csv")
    df_tripinfo = pd.concat([df_tripinfo, df], ignore_index=True)
    df_tripinfo.to_csv("tripinfo_fixed.csv")
    df = pd.read_csv(f"edgedata_{i}.csv")
    df_edgedata = pd.concat([df_edgedata, df], ignore_index=True)
    df_edgedata.to_csv("edgedata_fixed.csv")
