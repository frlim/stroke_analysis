# Summarize basic results
# Get percentage of patient-location scenarios that had the same/different destination V1 and V2

import pandas as pd
import data_io
from pathlib import Path
import numpy as np
import scipy.stats as stats

# Define patient subset
# pid_list = [i for j in (range(50,103), range(250, 325), range(326, 370), range(371,372), 
#             range(373,1000)) for i in j]
pid_list = [253]

# Load location-rural data
rural_loc = pd.read_csv("data/rural/cbsa_rural_locid.csv")
rural_loc = rural_loc.iloc[:,[0,-1]]
# Only look at first 500 locations
rural_loc = rural_loc.iloc[0:500,:]

# Summarize rural locations
rural_summ = rural_loc['is_rural'].mean() * 100
rural_data = {"Perc Rural": [rural_summ]}
rural_df = pd.DataFrame(rural_data)

# Load in closest hosp characteristic data
travel_time = pd.read_csv("data/hosp_characteristics/hosp_data_each_loc.csv")

# Patient Characteristics Distribution
stroke_patients_data = Path('/Volumes/dom_dgm_hur$/stroke_data/processed_data')
patients = pd.read_csv(stroke_patients_data/"patient_profiles_01_30_20.csv") # load patient profile data
# Only grab patients who are included in the analysis
patients = patients[patients.ID.isin(pid_list)]

# Get mean, median, std, min, max for age, nihss, time_since_symptoms from patient profile data
# summ_stats: summary statistics of entire patient population
summ_stats = patients[['age', 'nihss', 'time_since_symptoms']].describe()
summ_stats = summ_stats.iloc[[1,2,3,7],:]
med_array = [patients[x].median() for x in ['age', 'nihss', 'time_since_symptoms']]
summ_stats.loc['median'] = med_array
iqr_array = [str(np.percentile(patients[x], 25)) + " - " + str(np.percentile(patients[x], 75)) for x in ['age', 'nihss', 
                                                                                       'time_since_symptoms']]
summ_stats.loc['iqr'] = iqr_array

# Get number/perc female: 1 = female, 0 = male
summ_stats['sex (perc female)'] = [patients['sex'].mean() * 100, np.nan, np.nan, np.nan, np.nan, np.nan]

# Initialize lists: counts for each recommendation
changed_lst = []
unchanged_lst = []

psc_to_csc = []
csc_to_psc = []
group = []
csc = []
psc = []

# Initialize dictionary to count number of times each pid appears in each recommendation change
psc_to_csc_dict = {}
csc_to_psc_dict = {}
group_dict = {}
agree_dict = {}

# Initialize dictionary to count location id for each recommendation change
loc_psc_to_csc_dict = {}
loc_csc_to_psc_dict = {}
loc_group_dict = {}
loc_agree_dict = {}

# Initialize counts for number of V1 and V2 PSC/CSC recommendations
v1_psc_recs = 0
v1_csc_recs = 0
v2_psc_recs = 0
v2_csc_recs = 0

for pid in pid_list:
    # Get pathnanme for summarized csv file
    all_loc_path = list(data_io.BASIC_ANALYSIS_OUTPUT.glob(f'pid={pid}*_summarized.csv'))[0]

    # Read csv
    all_loc = pd.read_csv(all_loc_path)
    # Only look at first 500 locations
    all_loc = all_loc.iloc[0:500,:]

    # Get counts for CSC and PSC for V1 and V2 model
    if 'CSC' in all_loc['BestCenterType_be'].value_counts().index.tolist():
        v1_csc_recs += all_loc['BestCenterType_be'].value_counts()['CSC']
    if 'PSC' in all_loc['BestCenterType_be'].value_counts().index.tolist():
        v1_psc_recs += all_loc['BestCenterType_be'].value_counts()['PSC']
    if 'CSC' in all_loc['BestCenterType_af'].value_counts().index.tolist():
        v2_csc_recs += all_loc['BestCenterType_af'].value_counts()['CSC']
    if 'PSC' in all_loc['BestCenterType_af'].value_counts().index.tolist():
        v2_psc_recs += all_loc['BestCenterType_af'].value_counts()['PSC']

    # Dataframe of rows that had same or different hospital key
    unchanged = all_loc[all_loc['BestCenterKey_be']==all_loc['BestCenterKey_af']]
    changed = all_loc[all_loc['BestCenterKey_be']!=all_loc['BestCenterKey_af']]

    # Array of locids
    unchanged_locids = unchanged['Location'].unique()
    changed_locids = changed['Location'].unique()

    # Counts of the number of changed and unchanged hospital keys
    num_unchanged = unchanged.shape[0]
    num_changed = changed.shape[0]

    # Make sure for each pid, total number of 500 recommendations
    if num_unchanged + num_changed != 500:
        print("Error: Doesn't add to 500")

    # # Make sure for each pid, total number of 1000 recommendations
    # if num_unchanged + num_changed != 1000:
    #     print("Error: Doesn't add to 1000")
    
    # Further analysis into the changed recommendations
    # Look into how many hospital keys changed from psc to csc, csc to psc, or changed hospital key within same center type
    psc_to_csc_df = changed[(changed['BestCenterType_be']=='PSC') & (changed['BestCenterType_af']=='CSC')]
    num_psc_to_csc = psc_to_csc_df.shape[0]
    csc_to_psc_df = changed[(changed['BestCenterType_be']=='CSC') & (changed['BestCenterType_af']=='PSC')]
    num_csc_to_psc = csc_to_psc_df.shape[0]
    csc_within_df = changed[(changed['BestCenterType_be']=='CSC') & (changed['BestCenterType_af']=='CSC')]
    num_csc = csc_within_df.shape[0]
    psc_within_df = changed[(changed['BestCenterType_be']=='PSC') & (changed['BestCenterType_af']=='PSC')]
    num_psc = psc_within_df.shape[0]
    group_df = pd.concat([csc_within_df, psc_within_df], ignore_index=True)
    num_within_group = num_csc + num_psc

    # Make sure all these values add up to the number of changed center keys
    if num_psc_to_csc + num_csc_to_psc + num_within_group != num_changed:
        print("Error: Doesn't add to number of changed recommendations")
    
    # Add counts to list to later sum
    changed_lst.append(num_changed)
    unchanged_lst.append(num_unchanged)
    psc_to_csc.append(num_psc_to_csc)
    csc_to_psc.append(num_csc_to_psc)
    group.append(num_within_group)
    csc.append(num_csc)
    psc.append(num_psc)

    # Add pid to dictionary to count how many times pid appears for recommendation type change
    if pid not in psc_to_csc_dict:
        psc_to_csc_dict[pid] = num_psc_to_csc
    else:
        psc_to_csc_dict[pid] += num_psc_to_csc
    
    if pid not in csc_to_psc_dict:
        csc_to_psc_dict[pid] = num_csc_to_psc
    else:
        csc_to_psc_dict[pid] += num_csc_to_psc

    if pid not in group_dict:
        group_dict[pid] = num_within_group
    else:
        group_dict[pid] += num_within_group

    if pid not in agree_dict:
        agree_dict[pid] = num_unchanged
    else:
        agree_dict[pid] += num_unchanged
    
    # Add locid to dictionary to count how many times locid appears for recommendation type change
    for locid in unchanged['Location'].tolist():
        if locid not in loc_agree_dict:
            loc_agree_dict[locid] = 1
        else:
            loc_agree_dict[locid] += 1
   
    for locid in psc_to_csc_df['Location'].tolist():
        if locid not in loc_psc_to_csc_dict:
            loc_psc_to_csc_dict[locid] = 1
        else:
            loc_psc_to_csc_dict[locid] += 1

    for locid in csc_to_psc_df['Location'].tolist():
        if locid not in loc_csc_to_psc_dict:
            loc_csc_to_psc_dict[locid] = 1
        else:
            loc_csc_to_psc_dict[locid] += 1

    for locid in group_df['Location'].tolist():
        if locid not in loc_group_dict:
            loc_group_dict[locid] = 1
        else:
            loc_group_dict[locid] += 1

# Get number/perc of csc/psc recommendations for V1 and V2
# Double check that the number of recs is correct
v1_recs = v1_psc_recs + v1_csc_recs
v2_recs = v2_psc_recs + v2_csc_recs
if v1_recs != len(pid_list) * 500:
    print("Error: Number of V1 recommendations is incorrect")
if v2_recs != len(pid_list) * 500:
    print("Error: Number of V2 recommendations is incorrect")

# Create dataframe for output
rec_type = {'num_psc':[v1_psc_recs, v2_psc_recs],
        'num_csc':[v1_csc_recs, v2_csc_recs],
        "total_num":[v1_recs, v2_recs],
        "perc_psc":[round(v1_psc_recs/v1_recs * 100,1), round(v2_psc_recs/v2_recs * 100,1)],
        "perc_csc":[round(v1_csc_recs/v1_recs * 100,1), round(v2_csc_recs/v2_recs * 100,1)]}
rec_type_df = pd.DataFrame(rec_type, index=['V1', 'V2'])

# Initialize dataframe
# All changes
overall_df = pd.DataFrame()
overall_df['Num_Changed'] = [sum(changed_lst)]
overall_df['Num_Same'] = [sum(unchanged_lst)]
overall_df['Perc_Changed'] = [(sum(changed_lst) / (sum(changed_lst) + sum(unchanged_lst))) * 100]
overall_df['Perc_Same'] = [(sum(unchanged_lst) / (sum(changed_lst) + sum(unchanged_lst))) * 100]

# Further analysis of changes
changed_df = pd.DataFrame(columns=["Num", "Percent"])
changed_df.loc['CSC_to_PSC'] = [sum(csc_to_psc), (sum(csc_to_psc)/sum(changed_lst)) * 100]
changed_df.loc['PSC_to_CSC'] = [sum(psc_to_csc), (sum(psc_to_csc)/sum(changed_lst)) * 100]
changed_df.loc['Within_Group'] = [sum(group), (sum(group)/sum(changed_lst)) * 100]

# Characteristics stratified by V1/V2 agreement
# Grab patient information for each pid and build dataframe for each recommendation stage
# Duplicate patient rows for how many times a specific patient had that change/no change
psc_to_csc_df = pd.DataFrame(columns=patients.columns)
for key, value in psc_to_csc_dict.items():
    row = patients[patients['ID']==key]
    for i in range(0, value):
        psc_to_csc_df = pd.concat([psc_to_csc_df, row])

if psc_to_csc_df.shape[0] != sum(psc_to_csc):
    print("Error: Dataframe psc_to_csc_df does not have expected number of rows")

csc_to_psc_df = pd.DataFrame(columns=patients.columns)
for key, value in csc_to_psc_dict.items():
    row = patients[patients['ID']==key]
    for i in range(0, value):
        csc_to_psc_df = pd.concat([csc_to_psc_df, row])

if csc_to_psc_df.shape[0] != sum(csc_to_psc):
    print("Error: Dataframe csc_to_psc_df does not have expected number of rows")

group_df = pd.DataFrame(columns=patients.columns)
for key, value in group_dict.items():
    row = patients[patients['ID']==key]
    for i in range(0, value):
        group_df = pd.concat([group_df, row])

if group_df.shape[0] != sum(group):
    print("Error: Dataframe group_df does not have expected number of rows")

agree_df = pd.DataFrame(columns=patients.columns)
for key, value in agree_dict.items():
    row = patients[patients['ID']==key]
    for i in range(0, value):
        agree_df = pd.concat([agree_df, row])

if agree_df.shape[0] != sum(unchanged_lst):
    print("Error: Dataframe agree_df does not have expected number of rows")

# List of dataframes for each recommendation change containing pids and their information
all_df = [agree_df, psc_to_csc_df, csc_to_psc_df, group_df]

# Initialize char_df which will output V1/V2 agreement stratified by patient characteristics
char_df = pd.DataFrame(columns=["V1_V2_agree", "PSC_to_CSC", "CSC_to_PSC", "Within_group_change"])
# Get median age and IQR
age_array = [x['age'].median() for x in all_df]
age_iqr = [str(np.percentile(x['age'], 25)) + ' - ' + str(np.percentile(x['age'], 75)) for x in all_df]
char_df.loc['Median Age'] = age_array
char_df.loc['Median Age, IQR'] = age_iqr
# Perc female
sex_array = [x['sex'].sum() for x in all_df]
sex_perc = [x['sex'].mean() * 100 for x in all_df]
char_df.loc['Female, n'] = sex_array
char_df.loc['Female, %'] = sex_perc
# NIHSS median, IQR
nihss_med_array = [x['nihss'].median() for x in all_df]
nihss_iqr = [str(np.percentile(x['nihss'], 25)) + ' - ' + str(np.percentile(x['nihss'], 75)) for x in all_df]
char_df.loc['NIHSS median'] = nihss_med_array
char_df.loc['NIHSS median, IQR'] = nihss_iqr
# NIHSS mean, std
nihss_mean_array = [x['nihss'].mean() for x in all_df]
nihss_std = [x['nihss'].std() for x in all_df]
char_df.loc['NIHSS mean'] = nihss_mean_array
char_df.loc['NIHSS mean, std'] = nihss_std
# Time from LWK median, IQR
lwk_med_array = [x['time_since_symptoms'].median() for x in all_df]
lwk_med_iqr = [str(np.percentile(x['time_since_symptoms'], 25)) + ' - ' + str(np.percentile(x['time_since_symptoms'], 75)) for x in all_df]
char_df.loc['Time from LWK Median'] = lwk_med_array
char_df.loc['Time from LWK Median, IQR'] = lwk_med_iqr
# Time from LWK mean, std
lwk_mean_array = [x['time_since_symptoms'].mean() for x in all_df]
lwk_mean_std = [x['time_since_symptoms'].std() for x in all_df]
char_df.loc['Time from LWK Mean'] = lwk_mean_array
char_df.loc['Time from LWK Mean, SD'] = lwk_mean_std

# Location Analysis
# Rural locations
loc_agree_df = pd.DataFrame(columns=rural_loc.columns)
for key, value in loc_agree_dict.items():
    row = rural_loc[rural_loc['LOC_ID']==key]
    for i in range(0, value):
        loc_agree_df = pd.concat([loc_agree_df, row])

loc_psc_to_csc_df = pd.DataFrame(columns=rural_loc.columns)
for key, value in loc_psc_to_csc_dict.items():
    row = rural_loc[rural_loc['LOC_ID']==key]
    for i in range(0, value):
        loc_psc_to_csc_df = pd.concat([loc_psc_to_csc_df, row])

loc_csc_to_psc_df = pd.DataFrame(columns=rural_loc.columns)
for key, value in loc_csc_to_psc_dict.items():
    row = rural_loc[rural_loc['LOC_ID']==key]
    for i in range(0, value):
        loc_csc_to_psc_df = pd.concat([loc_csc_to_psc_df, row])

loc_group_df = pd.DataFrame(columns=rural_loc.columns)
for key, value in loc_group_dict.items():
    row = rural_loc[rural_loc['LOC_ID']==key]
    for i in range(0, value):
        loc_group_df = pd.concat([loc_group_df, row])

all_loc_df = [loc_agree_df, loc_psc_to_csc_df, loc_csc_to_psc_df, loc_group_df]
rural_array = [x['is_rural'].sum() for x in all_loc_df]
rural_perc = [x['is_rural'].mean() * 100 for x in all_loc_df]
char_df.loc['Rural Location, n'] = rural_array
char_df.loc['Rural Location, %'] = rural_perc

# Median travel time to closest PSC/CSC
# Closest hospital is PSC or CSC
# Median tPA for closest hospital
time_loc_agree_df = pd.DataFrame(columns=travel_time.columns)
for key, value in loc_agree_dict.items():
    row = travel_time[travel_time['loc_id']==key]
    for i in range(0, value):
        time_loc_agree_df = pd.concat([time_loc_agree_df, row])

time_loc_psc_to_csc_df = pd.DataFrame(columns=travel_time.columns)
for key, value in loc_psc_to_csc_dict.items():
    row = travel_time[travel_time['loc_id']==key]
    for i in range(0, value):
        time_loc_psc_to_csc_df = pd.concat([time_loc_psc_to_csc_df, row])

time_loc_csc_to_psc_df = pd.DataFrame(columns=travel_time.columns)
for key, value in loc_csc_to_psc_dict.items():
    row = travel_time[travel_time['loc_id']==key]
    for i in range(0, value):
        time_loc_csc_to_psc_df = pd.concat([time_loc_csc_to_psc_df, row])

time_loc_group_df = pd.DataFrame(columns=travel_time.columns)
for key, value in loc_group_dict.items():
    row = travel_time[travel_time['loc_id']==key]
    for i in range(0, value):
        time_loc_group_df = pd.concat([time_loc_group_df, row])

time_all_loc_df = [time_loc_agree_df, time_loc_psc_to_csc_df, time_loc_csc_to_psc_df, time_loc_group_df]
time_psc_array = [x['closest_psc_time'].median() for x in time_all_loc_df]
time_psc_iqr = [str(np.percentile(x['closest_psc_time'], 
                25)) + ' - ' + str(np.percentile(x['closest_psc_time'], 75)) for x in time_all_loc_df]
time_csc_array = [x['closest_csc_time'].median() for x in time_all_loc_df]
time_csc_iqr = [str(np.percentile(x['closest_csc_time'], 
                25)) + ' - ' + str(np.percentile(x['closest_csc_time'], 75)) for x in time_all_loc_df]
char_df.loc['Median Time to Closest PSC'] = time_psc_array
char_df.loc['Median Time to Closest PSC, IQR'] = time_psc_iqr
char_df.loc['Median Time to Closest CSC'] = time_csc_array
char_df.loc['Median Time to Closest CSC, IQR'] = time_csc_iqr

closest_hosp_csc = [x[x.closest_center =='CSC'].shape[0] for x in time_all_loc_df]
closest_hosp_psc = [x[x.closest_center =='PSC'].shape[0] for x in time_all_loc_df]
perc_closest_hosp_csc = [x[x.closest_center =='CSC'].shape[0]/x.shape[0] * 100 for x in time_all_loc_df]
perc_closest_hosp_psc = [x[x.closest_center =='PSC'].shape[0]/x.shape[0] * 100 for x in time_all_loc_df]
char_df.loc['Closest Hospital is PSC, n'] = closest_hosp_psc
char_df.loc['Closest Hospital is CSC, n'] = closest_hosp_csc
char_df.loc['Closest Hospital is PSC, %'] = perc_closest_hosp_psc
char_df.loc['Closest Hospital is CSC, %'] = perc_closest_hosp_csc

median_tpa = [x['IVTPA_MEDIAN'].median() for x in time_all_loc_df]
median_tpa_iqr = [str(np.nanpercentile(x['IVTPA_MEDIAN'], 
                25)) + ' - ' + str(np.nanpercentile(x['IVTPA_MEDIAN'], 75)) for x in time_all_loc_df]
char_df.loc['Median DTN time for tPA'] = median_tpa
char_df.loc['Median DTN time for tPA, IQR'] = median_tpa_iqr

# Write to Excel
with pd.ExcelWriter(str(data_io.SUMMARY_ANALYSIS_OUTPUT) + '/basic_summary_800p_061621.xlsx') as writer:  
    summ_stats.to_excel(writer, sheet_name ='Overall Patient Traits')
    rural_df.to_excel(writer, sheet_name="Rural Loc")
    rec_type_df.to_excel(writer, sheet_name='Rec Types')
    overall_df.to_excel(writer, sheet_name='Overall Recs')
    changed_df.to_excel(writer, sheet_name='Changed Recs')
    char_df.to_excel(writer, sheet_name='Stratified Characteristics')


