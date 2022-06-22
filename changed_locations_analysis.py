# changed_locations_analysis.py
# Purpose: Get the number of patients who changed for each location

import pandas as pd
import data_io

# Initialize dictionary for center key
loc_dict = {}
loc_dict['Locations'] = ["L" + str(num) for num in range(0,1000)]
loc_dict['No_Change'] = [0] * 1000 # Number of pid that didn't change for that location
loc_dict['PSC_to_CSC'] = [0] * 1000
loc_dict['CSC_to_PSC'] = [0] * 1000
loc_dict['Within_group_change'] = [0] * 1000
loc_dict['Changed'] = [0] * 1000 # Number of pid that did change for that location

def is_changed_key(row):
    if row['BestCenterKey_be'] != row['BestCenterKey_af']:
        return 1
    else:
        return 0

def is_PSC_to_CSC(row):
    if row['BestCenterType_be'] == "PSC" and row['BestCenterType_af'] == "CSC":
        return 1
    else:
        return 0

def is_CSC_to_PSC(row):
    if row['BestCenterType_be'] == "CSC" and row['BestCenterType_af'] == "PSC":
        return 1
    else:
        return 0

def is_within_group(row):
    if row['BestCenterKey_be'] != row['BestCenterKey_af']:
        if row['BestCenterType_be'] == row['BestCenterType_af']:
            return 1
        else:
            return 0
    else:
        return 0

for pid in [i for j in (range(250,294), range(500,581)) for i in j]:
    # Get pathnanme for summarized csv file
    all_loc_path = list(data_io.BASIC_ANALYSIS_OUTPUT.glob(f'pid={pid}*_summarized.csv'))[0]

    # Read csv
    all_loc = pd.read_csv(all_loc_path)

    # Add new column is_center_key_diff
    # 1: if center key changes, 0: if center key stays the same
    all_loc['is_center_key_diff'] = all_loc.apply(lambda row: is_changed_key(row), axis=1)
    # Add new column is_psc_to_csc
    all_loc['is_psc_to_csc'] = all_loc.apply(lambda row: is_PSC_to_CSC(row), axis=1)
    # Add new column is_csc_to_psc
    all_loc['is_csc_to_psc'] = all_loc.apply(lambda row: is_CSC_to_PSC(row), axis=1)
    # Add new column is_within_group
    all_loc['is_within_group_change'] = all_loc.apply(lambda row: is_within_group(row), axis=1)

    changed_list = all_loc['is_center_key_diff'].tolist()
    unchanged_list = [1 - val for val in changed_list] # take inverse
    psc_to_csc_list = all_loc['is_psc_to_csc'].tolist()
    csc_to_psc_list = all_loc['is_csc_to_psc'].tolist()
    within_group_list = all_loc['is_within_group_change'].tolist()

    # Add to dictionary
    loc_dict['Changed'] = [sum(x) for x in zip(loc_dict['Changed'], changed_list)]
    loc_dict['No_Change'] = [sum(x) for x in zip(loc_dict['No_Change'], unchanged_list)]
    loc_dict['PSC_to_CSC'] = [sum(x) for x in zip(loc_dict['PSC_to_CSC'], psc_to_csc_list)]
    loc_dict['CSC_to_PSC'] = [sum(x) for x in zip(loc_dict['CSC_to_PSC'], csc_to_psc_list)]
    loc_dict['Within_group_change'] = [sum(x) for x in zip(loc_dict['Within_group_change'], within_group_list)]

# Convert loc_dict to dataframe
loc_df = pd.DataFrame.from_dict(loc_dict)
# Add column: proportion of patients who had a changed recommendation
loc_df["Prop_Changed"] = loc_df['Changed'] / (loc_df['Changed'] + loc_df['No_Change'])
changed_loc_df = loc_df.copy()

loc_df = loc_df[['Locations', 'No_Change', 'Changed', 'Prop_Changed']]

changed_loc_df = changed_loc_df[changed_loc_df['Changed'] != 0]
changed_loc_df['Prop_PSC_to_CSC'] = changed_loc_df['PSC_to_CSC'] / changed_loc_df['Changed'] # denom out of change
changed_loc_df['Prop_CSC_to_PSC'] = changed_loc_df['CSC_to_PSC'] / changed_loc_df['Changed']
changed_loc_df['Prop_Within_Group_Change'] = changed_loc_df['Within_group_change'] / changed_loc_df['Changed']
changed_loc_df = changed_loc_df[['Locations', 'Changed', 'PSC_to_CSC', 'CSC_to_PSC', 'Within_group_change',
                                    'Prop_PSC_to_CSC', 'Prop_CSC_to_PSC', 'Prop_Within_Group_Change']]

# Write to Excel
with pd.ExcelWriter(str(data_io.LOCATION_ANALYSIS_OUTPUT) + '/location_key_changes.xlsx') as writer:  
    loc_df.to_excel(writer, sheet_name ='Overall', index=False)
    changed_loc_df.to_excel(writer, sheet_name='Changed Only', index=False)


