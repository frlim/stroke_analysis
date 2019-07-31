import pandas as pd
import data_io
import xlwings
import numpy as np
import column_names as cols



dtn = pd.read_excel(data_io.PROCESSED_DATA/'deidentified_DTN_master.xlsx')
keys = pd.read_csv(data_io.PROCESSED_DATA/'strokecenter_keys_master.csv')
addy = pd.read_csv(data_io.PROCESSED_DATA/'strokecenter_address_master.csv')

select_state = 'MA' # 2 letter abbrevation

# Partition tables by state of choice
state_mask = addy.State==select_state
#user inner join to select sub result
result = dtn.merge(keys,on='HOSP_KEY').merge(addy[state_mask],on='HOSP_ID',suffixes=('_keys','_addy'))
# Save lists with state abbrevation
# dtn.loc[dtn.HOSP_KEY.isin(result.HOSP_KEY),:].to_csv(data_io.PROCESSED_DATA/f'deidentified_DTN_{select_state}.csv',index=False)
# keys.loc[keys.HOSP_ID.isin(result.HOSP_ID),:].to_csv(data_io.PROCESSED_DATA/f'strokecenterl_keys_{select_state}.csv',index=False)
addy.loc[addy.HOSP_ID.isin(result.HOSP_ID),:].to_csv(data_io.PROCESSED_DATA/f'strokecenter_address_{select_state}.csv',index=False)

# review results
# dtn_r = pd.read_csv(data_io.PROCESSED_DATA/f'deidentified_DTN_{select_state}.csv')
# keys_r = pd.read_csv(data_io.PROCESSED_DATA/f'strokecenter_keys_{select_state}.csv')
addy_r = pd.read_csv(data_io.PROCESSED_DATA/f'strokecenter_address_{select_state}.csv')
# keys_r.Source.value_counts()
addy_r.Source.value_counts()

# Reformat hospitla address to work with stroke_locations
addy_r.rename({'Address':'Source_Address','Hospital Name':'OrganizationName','Zipcode':'PostalCode'},axis=1,inplace=True)
cols_to_add = ['Failed_Lookup','Name','Address','Latitude','Longitude','destination','destinationID','transfer_time']
for c in cols_to_add:
    addy_r[c] = np.nan

# stroke_locations require table to use '|' seperator instead of comma
# because later when we search for Google address they are commans in the string
addy_r.to_csv(data_io.PROCESSED_DATA/f'strokecenter_address_{select_state}_for_stroke_locations.csv',sep='|',index=False)
