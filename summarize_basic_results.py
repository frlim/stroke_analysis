# Summarize basic results
# Get percentage of patient-location scenarios that had the same/different destination V1 and V2

import pandas as pd
import data_io

# Initialize lists
changed_lst = []
unchanged_lst = []

psc_to_csc = []
csc_to_psc = []
group = []
csc = []
psc = []

for pid in range(250,276):
    # Get pathnanme for summarized csv file
    all_loc_path = list(data_io.BASIC_ANALYSIS_OUTPUT.glob(f'pid={pid}*_summarized.csv'))[0]

    # Read csv
    all_loc = pd.read_csv(all_loc_path)

    # Sum counts
    unchanged = all_loc[all_loc['BestCenterKey_be']==all_loc['BestCenterKey_af']]
    changed = all_loc[all_loc['BestCenterKey_be']!=all_loc['BestCenterKey_af']]

    num_unchanged = unchanged.shape[0]
    num_changed = changed.shape[0]

    if num_unchanged + num_changed != 1000:
        print("Error: Doesn't add to 1000")
    
    # Further analysis into the changed recommendations
    num_psc_to_csc = changed[(changed['BestCenterType_be']=='PSC') & (changed['BestCenterType_af']=='CSC')].shape[0]
    num_csc_to_psc = changed[(changed['BestCenterType_be']=='CSC') & (changed['BestCenterType_af']=='PSC')].shape[0]
    num_csc = changed[(changed['BestCenterType_be']=='CSC') & (changed['BestCenterType_af']=='CSC')].shape[0]
    num_psc = changed[(changed['BestCenterType_be']=='PSC') & (changed['BestCenterType_af']=='PSC')].shape[0]
    num_within_group = num_csc + num_psc

    if num_psc_to_csc + num_csc_to_psc + num_within_group != num_changed:
        print("Error: Doesn't add to number of changed recommendations")
    
    changed_lst.append(num_changed)
    unchanged_lst.append(num_unchanged)
    psc_to_csc.append(num_psc_to_csc)
    csc_to_psc.append(num_csc_to_psc)
    group.append(num_within_group)
    csc.append(num_csc)
    psc.append(num_psc)

# Initialize dataframe
overall_df = pd.DataFrame()
overall_df['Num_Changed'] = [sum(changed_lst)]
overall_df['Num_Same'] = [sum(unchanged_lst)]
overall_df['Perc_Changed'] = [(sum(changed_lst) / (sum(changed_lst) + sum(unchanged_lst))) * 100]
overall_df['Perc_Same'] = [(sum(unchanged_lst) / (sum(changed_lst) + sum(unchanged_lst))) * 100]

changed_df = pd.DataFrame(columns=["Num", "Percent"])
changed_df.loc['CSC_to_PSC'] = [sum(csc_to_psc), (sum(csc_to_psc)/sum(changed_lst)) * 100]
changed_df.loc['PSC_to_CSC'] = [sum(psc_to_csc), (sum(psc_to_csc)/sum(changed_lst)) * 100]
changed_df.loc['Within_Group'] = [sum(group), (sum(group)/sum(changed_lst)) * 100]

# Write to Excel
with pd.ExcelWriter(str(data_io.SUMMARY_ANALYSIS_OUTPUT) + '/basic_summary.xlsx') as writer:  
    overall_df.to_excel(writer, sheet_name='Overall')
    changed_df.to_excel(writer, sheet_name='Changed')

