# changed_locations_analysis.py
# Purpose: Get the number of patients who changed for each location

import pandas as pd
import data_io
import time
from tqdm import tqdm

start_time = time.time()

# Initialize dictionary for center key
loc_dict = {}
loc_dict['Locations'] = ["L" + str(num) for num in range(0,1000)]
loc_dict['No_Change'] = [0] * 1000 # Number of pid that didn't change for that location
loc_dict['Changed'] = [0] * 1000 # Number of pid that did change for that location

def is_changed_key(row):
    if row['BestCenterKey_be'] != row['BestCenterKey_af']:
        return 1
    else:
        return 0

for pid in tqdm(range(250,276)):
    # Get pathnanme for summarized csv file
    all_loc_path = list(data_io.BASIC_ANALYSIS_OUTPUT.glob(f'pid={pid}*_summarized.csv'))[0]

    # Read csv
    all_loc = pd.read_csv(all_loc_path)

    # Add new column is_center_key_diff
    # 1: if center key changes, 0: if center key stays the same
    all_loc['is_center_key_diff'] = all_loc.apply(lambda row: is_changed_key(row), axis=1)

    changed_list = all_loc['is_center_key_diff'].tolist()
    unchanged_list = [1 - val for val in changed_list] # take inverse

    # Add to dictionary
    loc_dict['Changed'] = [sum(x) for x in zip(loc_dict['Changed'], changed_list)]
    loc_dict['No_Change'] = [sum(x) for x in zip(loc_dict['No_Change'], unchanged_list)]

# Convert loc_dict to dataframe
loc_df = pd.DataFrame.from_dict(loc_dict)
# Add column: proportion of patients who had a changed recommendation
loc_df["Prop_Changed"] = loc_df['Changed'] / (loc_df['Changed'] + loc_df['No_Change'])

# Write to csv
loc_df.to_csv(str(data_io.LOCATION_ANALYSIS_OUTPUT) + '/location_key_changes.csv')

print("changed_locations_analysis.py took", time.time() - start_time, "to run")

