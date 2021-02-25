# Aggregate diff_QALY for _changed.csv outputs for all patients at each location
# TODO: some QALYs are missing in certain before strategies

import pandas as pd
import data_io
import numpy as np

# Initialize dictionary for each location
loc_dict = {}

for pid in [i for j in (range(250,294), range(500,581)) for i in j]:
    # Get pathnanme for changed csv file
    all_loc_path = list(data_io.BASIC_ANALYSIS_OUTPUT.glob(f'pid={pid}*_changed.csv'))[0]

    # Read csv
    all_loc = pd.read_csv(all_loc_path, index_col="Location")

    if all_loc.shape[0] != 0: # only if changes exist, run code
        # Remove location if no before qalys reported
        all_loc = all_loc.dropna()

        for loc_id in all_loc.index:
            if loc_id not in loc_dict: # add location to dictionary if key doesn't exist
                loc_dict[loc_id] = np.array([all_loc.loc[loc_id, "diff_QALY"]])
            else:
                loc_dict[loc_id] = np.append(loc_dict[loc_id], all_loc.loc[loc_id, "diff_QALY"])
        
# Aggregate QALYs for each location
# Initialize dataframe
df = pd.DataFrame(columns=["mean_diff_qaly", "std_diff_qaly", "med_diff_qaly", "iqr_diff_qaly"])

for loc_id in loc_dict.keys():
    df.loc[loc_id, "mean_diff_qaly"] = np.mean(np.array(loc_dict[loc_id]))
    df.loc[loc_id, "std_diff_qaly"] = np.std(np.array(loc_dict[loc_id]))
    df.loc[loc_id, "med_diff_qaly"] = np.median(np.array(loc_dict[loc_id]))
    df.loc[loc_id, 'iqr_diff_qaly'] = str(np.percentile(np.array(loc_dict[loc_id]), 25)) + " - " + str(
                             np.percentile(np.array(loc_dict[loc_id]), 75))
# Reorder index
loc_lst = ["L" + str(num) for num in range(0,1000)]
new_lst = []
for i in loc_lst:
    if i in loc_dict.keys():
        new_lst.append(i)

df = df.reindex(new_lst)

# Write to Excel
df.to_excel(str(data_io.SUMMARY_ANALYSIS_OUTPUT) + '/qaly_loc_summary_2_25_21.xlsx')