import pandas as pd
import data_io
import xlwings
import numpy as np
import column_names as cols

addy = pd.read_csv(data_io.PROCESSED_DATA / 'hospital_address_NE_v2.csv',dtype=str)
addy.rename(
    {
        'Address': 'Source_Address',
        'Hospital Name': 'OrganizationName',
        'Zipcode': 'PostalCode'
    },
    axis=1,
    inplace=True)
cols_to_add = [
    'Failed_Lookup', 'Name', 'Address', 'Latitude', 'Longitude', 'destination',
    'destinationID', 'transfer_time'
]
for c in cols_to_add:
    addy[c] = np.nan

# stroke_locations require table to use '|' seperator instead of comma
# because later when we search for Google address they are commands in the string
addy.to_csv(data_io.PROCESSED_DATA /
              f'hospital_address_NE_for_stroke_locations_v2.csv',
              sep='|',
              index=False)


# if only want hospital for a single state -> not recommnend
# since patients can still go to hospitals from another state

select_state = 'MA'  # 2 letter abbrevatio

# Partition tables by state of choice
state_mask = addy.State == select_state
# Save lists with state abbrevation
addy.loc[state_mask, :].to_csv(data_io.PROCESSED_DATA /
                               f'hospital_address_{select_state}_v2.csv',
                               index=False)

# review results
# dtn_r = pd.read_csv(data_io.PROCESSED_DATA/f'deidentified_DTN_{select_state}.csv')
# keys_r = pd.read_csv(data_io.PROCESSED_DATA/f'strokecenter_keys_{select_state}.csv')
addy_r = pd.read_csv(data_io.PROCESSED_DATA /
                     f'strokecenter_address_{select_state}.csv')
# keys_r.Source.value_counts()
addy_r.Source.value_counts()

# Reformat hospitla address to work with stroke_locations
addy_r.rename(
    {
        'Address': 'Source_Address',
        'Hospital Name': 'OrganizationName',
        'Zipcode': 'PostalCode'
    },
    axis=1,
    inplace=True)
cols_to_add = [
    'Failed_Lookup', 'Name', 'Address', 'Latitude', 'Longitude', 'destination',
    'destinationID', 'transfer_time'
]
for c in cols_to_add:
    addy_r[c] = np.nan

# stroke_locations require table to use '|' seperator instead of comma
# because later when we search for Google address they are commans in the string
addy_r.to_csv(data_io.PROCESSED_DATA /
              f'strokecenter_address_{select_state}_for_stroke_locations.csv',
              sep='|',
              index=False)
