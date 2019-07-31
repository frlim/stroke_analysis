import pandas as pd
from pathlib import Path
import xlwings as xw
import data_io
import column_names as colnames

# Get kori grant
kori_grant = data_io.cleaned_KORI_GRANT()

# Get hospital lists
hosp_keys = pd.read_csv(data_io.PROCESSED_DATA / 'hospital_keys_master.csv')
hosp_address = pd.read_csv(
    data_io.PROCESSED_DATA / 'hospital_address_master.csv')

# Generate deidentified_DTN
dtn_aha = kori_grant.copy()
# Cap at 270 mins for TPA
for col in colnames.tpa_time_cols:
    dtn_aha.loc[dtn_aha[col] > 270, col] = 270
# We'd only have data for some hospital
# hosp_id of hosp_key is in string since some hospital have weird IDS
dtn_aha['AHA_ID'] = dtn_aha['AHA_ID'].astype(int).astype(str)
hosp_keys['AHA_ID'] = hosp_keys['AHA_ID'].astype(
    int, errors='ignore').astype(str)
# join using AHA_ID
# in hospital_keys there are hospitals with AHA_ID and defined CenterType thanks
# to merging with JCC list back in create_hosp_keys_and_address.py
dtn_master = dtn_aha.merge(
    hosp_keys[['HOSP_ID', 'AHA_ID', 'HOSP_KEY']],
    on='AHA_ID',
    how='outer',
    indicator=True)
#Check merge results
dtn_master['_merge'].value_counts()
dtn_master.drop(['HOSP_ID', '_merge'], axis=1, inplace=True)

# generate center type, transfer JCC centerType to dtn
jc_hosp_centertype = hosp_address.loc[hosp_address.Source ==
                                      'Joint Commission',
                                      ['HOSP_ID', 'CenterType']].merge(
                                          hosp_keys[['HOSP_ID', 'HOSP_KEY']])
dtn_master = dtn_master.merge(
    jc_hosp_centertype, on='HOSP_KEY', how='outer',indicator='_from_jc')
dtn_master['_from_jc'].value_counts()
dtn_master._from_jc=dtn_master._from_jc.map({'right_only':True,'left_only':False,'both':True})

# Check to make sure not zero (should be 81)
(~(dtn_master.AHA_ID == 'nan') & dtn_master.CenterType.notna()).sum()

# figure out center type for hospitals with DTN
have_dtn_m = dtn_master[colnames.tpa_time_cols].notna().all(
    axis=1) | dtn_master[colnames.evt_time_cols].notna().all(axis=1)
# filter out hospitals that are not stroke center: criteria is
# hospital is from JC list OR hospital has time data in DTN
stroke_center_m = have_dtn_m | dtn_master._from_jc
stroke_center_m.sum()
dtn_master = dtn_master[stroke_center_m]
hosp_keys = hosp_keys[hosp_keys.HOSP_KEY.isin(dtn_master.HOSP_KEY)]
hosp_address = hosp_address[hosp_address.HOSP_ID.isin(hosp_keys.HOSP_ID)]

# Fill in Center Type for DTN
have_tpa_m = have_dtn_m & dtn_master[colnames.tpa_time_cols].notna().all(
    axis=1)
have_evt_m = have_dtn_m & dtn_master[colnames.evt_time_cols].notna().all(
    axis=1)
dtn_master.loc[have_tpa_m, 'CenterType'] = 'Primary'
dtn_master.loc[have_evt_m, 'CenterType'] = 'Comprehensive'
dtn_master.loc[dtn_master.CenterType.isna(), 'CenterType'] = 'Primary'

# reassign centertype values to  hospital address centertype
hosp_address_out=hosp_address.merge(hosp_keys[['HOSP_ID','HOSP_KEY']],on='HOSP_ID').merge(
dtn_master[['HOSP_KEY','CenterType']],how='outer',on='HOSP_KEY',suffixes=('_addy','_dtn'))
hosp_address_out.rename({'CenterType_dtn':'CenterType'},axis=1,inplace=True)
hosp_address_out.drop(['CenterType_addy','HOSP_KEY'],axis=1,inplace=True)
hosp_address_out.to_csv(data_io.PROCESSED_DATA/'strokecenter_address_master.csv',index=False)
hosp_keys.to_csv(data_io.PROCESSED_DATA/'strokecenter_keys_master.csv',index=False)

# drop identifiable ID columns
dtn_master.drop(['AHA_ID', 'HOSP_ID', 'SITE_ID'], axis=1, inplace=True)
dtn_master.head()

# For hospitals w missing DTN, put in average time
dtn_master.loc[~have_tpa_m & (
    dtn_master.CenterType == 'Primary'), colnames.tpa_time_cols] = (47, 61, 83)
dtn_master.loc[~have_tpa_m & (
    dtn_master.CenterType == 'Comprehensive'), colnames.tpa_time_cols] = (39,
                                                                          52,
                                                                          70)
dtn_master.loc[~have_evt_m & (
    dtn_master.CenterType == 'Comprehensive'), colnames.evt_time_cols] = (83,
                                                                          145,
                                                                          192)

# Add data_source col
dtn_master.loc[~have_tpa_m, 'TPA_SOURCE'] = 'national average'
dtn_master.loc[have_tpa_m, 'TPA_SOURCE'] = 'collected'
dtn_master.loc[~have_evt_m & (dtn_master.CenterType == 'Comprehensive'
                              ), 'EVT_SOURCE'] = 'national average'
dtn_master.loc[have_evt_m & (
    dtn_master.CenterType == 'Comprehensive'), 'EVT_SOURCE'] = 'collected'

# Save tables as excel file
# Optional step: encrypt sheets with passwords in Excel
dtn_master.to_excel(
    data_io.PROCESSED_DATA / 'deidentified_DTN_master.xlsx', index=False)
