import pandas as pd
import xlwings as xw
import numpy as np
import data_io

# load KORI_GRANT, excel will popup and ask for password
dtn = data_io.DTN(dtn_file=data_io.PROCESSED_DATA / 'deidentified_DTN_trial.xlsx',cell_range='A1:AC244')

# figure out center type
prim_center_filter = dtn['ARTPUNC_N'].isna() | dtn['ARTPUNC_P75'].isna() | dtn['ARTPUNC_P25'].isna() | dtn['ARTPUNC_MEDIAN'].isna()
prim_center_filter = dtn['IATPA_N'].isna() | dtn['IATPA_P75'].isna() | dtn['IATPA_P25'].isna() | dtn['IATPA_MEDIAN'].isna()
dtn['CENTER_TYPE'] = 'Comprehensive'
dtn.loc[prim_center_filter,'CENTER_TYPE'] = 'Primary'
# KORI_GRANT said 36 CSC but only 31 seems to ARTPUNCH time
dtn['CENTER_TYPE'].value_counts()


# AHA_ID and hospital adddress look up
aha_address = pd.read_excel(file_path/'AHA 2012 ID codes.xlsx',header=None,names=['AHA_ID','Name','Street','City',
'Postal_Code','State'])

# cross-list data in both spreadsheets
merge = aha_address.merge(dtn[['AHA_ID','SITE_ID','CENTER_TYPE']],on='AHA_ID',how='inner')
merge['Failed_Lookup'] = False
merge['Latitude'] = np.nan
merge['Longitude'] = np.nan


# rename columns so that it'll be similar to Patrick's input
# purpose: so file is compatible with hospitals.update_locations_han()
merge.columns = ['AHA_ID','OrganizationName','Street','City','PostalCode','State','SITE_ID','CenterType'
'Failed_Lookup','Latitude','Longitude']
merge.to_csv(file_path/'inner_join_siteID.csv',index=False)

# review output
df = pd.read_csv(file_path/'inner_join_siteID.csv',sep='|')
df.head()
