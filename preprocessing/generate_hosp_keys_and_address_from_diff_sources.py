import pandas as pd
import data_io
import numpy as np
import column_names as colnames

OUTPUT_COLS_ORDER = [
    'HOSP_ID', 'Hospital Name', 'Address', 'City', 'Zipcode', 'State',
    'CenterType', 'Source', 'Original_ID_Name', 'OrganizationId', 'AHA_ID'
]

#1ST SOURCE-----------------------------------------------------------------
# Get JC stroke certification list (use modified download module from stroke_locations)
jc_data = data_io.JC_StrokeCetification()
# Cleaning
jc_data.drop_duplicates(inplace=True)
program_map = {
    'Advanced Comprehensive Stroke Center': 'Comprehensive',
    'Advanced Primary Stroke Center': 'Primary',
    # Treatment of TSCs is undecided; taking conservative approach
    'Advanced Thrombectomy Capable Stroke Ctr': 'Primary',
}
jc_data['CenterType'] = jc_data.CertificationProgram.str.strip().map(
    program_map)
jc_data = jc_data.dropna()
jc_data['Source'] = 'Joint Commission'

# Comprehensive centers get listed twice in JC list:
# one for primary certification and second one for Comprehensive
# Remove Primary entries if Comprehensive is available
jc_data['_CenterTypeCode'] = jc_data['CenterType'].map({
    'Comprehensive': 1,
    'Primary': 0
})

# Take the first max , which will prevent duplicates produced by 2 programs both map to Primary
jc_data = jc_data.groupby([
    'OrganizationName', 'City', 'PostalCode', 'State'
]).apply(lambda x: x.loc[x._CenterTypeCode == x._CenterTypeCode.max(), :].iloc[
    0, :]).reset_index(drop=True)
jc_data.drop(['_CenterTypeCode'], axis=1, inplace=True)

# Reshape and rename to match other sources we're loading later on
jc_data.drop([
    'Program', 'CertificationProgram', 'CertificationDecision', 'EffectiveDate'
],
             axis=1,
             inplace=True)
jc_data.columns = [
    'OrganizationId', 'Hospital Name', 'City', 'State', 'Zipcode',
    'CenterType', 'Source'
]

# Fill in default values for columns we dont have
jc_data['Address'] = np.nan
jc_data['Original_ID_Name'] = 'OrganizationId'
jc_data['HOSP_ID'] = jc_data.OrganizationId
jc_data['AHA_ID'] = np.nan
# Rearrange columns order to match format we want
jc_data = jc_data[OUTPUT_COLS_ORDER]
# Check to make sure every center is only listed once
# Should return True
(jc_data.groupby(['Hospital Name', 'City', 'Zipcode',
                  'State']).size() == 1).all()

# 2ND SOURCE-----------------------------------------------------------------
# Get list of AHA hospitals, retrieved from Kori
aha_address = pd.read_excel(data_io.RAW_DATA / 'AHA ID List Northeast.xlsx',
                            dtype=str)
# change column names to match format we want
aha_address.drop('Status', axis=1, inplace=True)
aha_address.rename(columns={
    'City Name': 'City',
    'Zipcode 2': 'Zipcode',
    'AHA ID': 'AHA_ID'
},
                   inplace=True)
aha_address['HOSP_ID'] = aha_address.AHA_ID
aha_address['OrganizationId'] = np.nan
# Cleaning - remove city and state from hosp name
aha_address['Hospital Name'] = aha_address['Hospital Name'].apply(
    lambda x: str(x).split('_')[0])
aha_address['Original_ID_Name'] = 'AHA ID'
aha_address['CenterType'] = np.nan
aha_address['Source'] = 'AHA ID List Northeast'
aha_address = aha_address[OUTPUT_COLS_ORDER]

# 3RD SOURCE-----------------------------------------------------------------
# Get Kori's List of MA hospitals
address_cols = [
    'HOSP_ID', 'Hospital Name', 'Address', 'City', 'Zipcode', 'State'
]
aha_ma_address = pd.read_excel(data_io.RAW_DATA / 'AHA 2012 ID codes.xlsx',
                               names=address_cols,
                               dtype=str,
                               header=None)
aha_ma_address['AHA_ID'] = aha_ma_address.HOSP_ID
aha_ma_address['OrganizationId'] = np.nan
aha_ma_address['Original_ID_Name'] = 'AHA_ID'
aha_ma_address['CenterType'] = np.nan
aha_ma_address['Source'] = 'AHA 2012 ID codes'
aha_ma_address = aha_ma_address[OUTPUT_COLS_ORDER]

# 4TH SOURCE-----------------------------------------------------------------
# get missing address spreadsheet
aha_missing_ne = pd.read_excel(data_io.RAW_DATA / 'Missing AHA IDs NE.xlsx',
                               dtype=str)
aha_missing_ne.columns = [
    'HOSP_ID', 'Hospital Name', 'Address', 'City', 'State', 'Zipcode'
]
address_cols = [
    'HOSP_ID', 'Hospital Name', 'Address', 'City', 'Zipcode', 'State'
]
aha_missing_ne = aha_missing_ne[address_cols]
aha_missing_ne['AHA_ID'] = aha_missing_ne.HOSP_ID
aha_missing_ne['OrganizationId'] = np.nan
aha_missing_ne['Original_ID_Name'] = 'AHA_ID'
aha_missing_ne['CenterType'] = np.nan
aha_missing_ne['Source'] = 'Missing AHA IDs NE'

# COMBINING AHA SOURCES (2ND,3RD,4TH) TOGETHER---------------------------------
# Find what's missing in the other lists
aha_ma_address_for_append = aha_ma_address[~aha_ma_address['HOSP_ID'].
                                           isin(aha_address['HOSP_ID'])]
aha_missing_ne_for_append = aha_missing_ne[~(
    aha_missing_ne.HOSP_ID.isin(aha_address.HOSP_ID)
    | aha_missing_ne.HOSP_ID.isin(aha_ma_address))]
# Combine all 3 into one df
aha_address_total = pd.concat(
    [aha_address, aha_ma_address_for_append, aha_missing_ne_for_append])
# Not every hospital in these addresses are stroke centers
# Have to cross list with DTN file to get stroke centers
DTN = data_io.cleaned_KORI_GRANT()
DTN.AHA_ID = DTN.AHA_ID.astype(int).astype(str)
DTN.SITE_ID = DTN.SITE_ID.astype(int).astype(str)
aha_address_total = aha_address_total[aha_address_total.HOSP_ID.isin(
    DTN.AHA_ID)]

# 5TH SOURCE-----------------------------------------------------------------
# any hospital in DTN that havent been identified yet
DTN_for_append = DTN[~DTN.AHA_ID.isin(aha_address_total.HOSP_ID)]
# Reformat into columns we want
DTN_for_append = DTN_for_append.loc[:, DTN_for_append.columns == 'AHA_ID']
DTN_for_append['HOSP_ID'] = DTN_for_append.AHA_ID
DTN_for_append['Source'] = 'KORI_GRANT'
DTN_for_append['Original_ID_Name'] = 'AHA_ID'

# COMBINING AHA & DTN SOURCES TOGETHER---------------------------------
aha_dtn_address_total = pd.concat([aha_address_total, DTN_for_append])

# Determine CenterType from DTN data
is_primary_m = DTN[colnames.evt_time_cols].isna().all(axis=1)
primary_AHA_IDs = DTN.AHA_ID[is_primary_m]
comp_AHA_IDs = DTN.AHA_ID[~is_primary_m]
aha_dtn_address_total.loc[aha_dtn_address_total.AHA_ID.
                          isin(primary_AHA_IDs), 'CenterType'] = 'Primary'
aha_dtn_address_total.loc[aha_dtn_address_total.AHA_ID.
                          isin(comp_AHA_IDs), 'CenterType'] = 'Comprehensive'

# COMBINING AHA+DTN WITH JC TOGETHER---------------------------------
# Identify hospitals that are both listed on AHA+DTN and JC
keep_only_general_zip = lambda x: str(x).split('-')[0]
aha_dtn_address_total['_zip'] = aha_dtn_address_total.Zipcode.apply(
    keep_only_general_zip)
aha_dtn_address_total.loc[aha_dtn_address_total._zip == 'nan', '_zip'] = np.nan
jc_data['_zip'] = jc_data.Zipcode.apply(keep_only_general_zip)
jc_data.loc[jc_data._zip == 'nan', '_zip'] = np.nan
# Join by city,state and zipcode to get a list of potentials
jc_aha = jc_data.merge(aha_dtn_address_total,
                       on=['City', 'State', '_zip'],
                       suffixes=('_jc', '_aha')).drop('_zip', axis=1)
# Manually compare since there's only ~100 centers
# Search on Google Maps to see if Hospital Name_x and Hospital Name_y are the same place
# Create column 'Same?', and put True/False down for each row
jc_aha.to_csv(data_io.PROCESSED_DATA / 'jc_aha.csv', index=False)
# # If want to use Google Maps to compare instead
# aha_cols_for_search = [
#     'HOSP_ID_y', 'Hospital Name_y', 'City', 'State', 'Zipcode_y',
#     'Source_y', 'AHA_ID_y'
# ]
# jc_cols_for_search = [
#     'HOSP_ID_x', 'Hospital Name_x', 'City', 'State', 'Zipcode_x',
#     'Source_x', 'Original_ID_Name_x'
# ]
# jc_for_search = jc_aha[jc_cols_for_search].drop_duplicates().reset_index(drop=True)
# jc_for_search.shape
# aha_cols_for_search = [
#     'HOSP_ID_y', 'Hospital Name_y', 'City', 'State', 'Zipcode_y',
#     'Source_y', 'AHA_ID_y'
# ]
# aha_for_search = jc_aha[aha_cols_for_search].drop_duplicates().reset_index(drop=True)
# use google Maps to get latitude + longitude of _x and _y, see if they are the same

# Read manually compared file
jc_aha_searched = pd.read_csv(data_io.PROCESSED_DATA /
                              'jc_aha_manual_searched_v2.csv',
                              dtype=str)
jc_aha_searched['Same?'] = jc_aha_searched['Same?'].map({
    'TRUE': True,
    'FALSE': False
})
jc_aha_shared = jc_aha_searched[jc_aha_searched['Same?']]
# jc_aha_shared[jc_aha_shared.HOSP_ID_aha.isin(['6220200','6220190'])]

# Remove the ones that are shared in JC list because
#  usually AHA list have more accurate hospital name
# (ex: St. Joseph's Hospital instead of VHS Accquisition No.5 )
jc_data_for_append = jc_data[~jc_data.HOSP_ID.isin(jc_aha_shared.HOSP_ID_jc)]
# jc_data_for_append[jc_data_for_append.HOSP_ID.isin(['5916','5915'])]

# Appending
address_out = pd.concat([aha_dtn_address_total, jc_data_for_append],
                        ignore_index=True)
# for shared hospitals, extract CenterType from JC since it's more accurate then CenterType from DTN
# we're rewriting them with JC CenterType
jc_aha_shared_JC_CenterType = jc_aha_shared[['HOSP_ID_aha', 'CenterType_jc']]
# jc_aha_shared_JC_CenterType[jc_aha_shared_JC_CenterType.HOSP_ID_aha.isin(['6220200','6220190'])]
address_out = address_out.merge(jc_aha_shared_JC_CenterType,
                                left_on='AHA_ID',
                                right_on='HOSP_ID_aha',
                                how='left')
address_out.loc[address_out.CenterType_jc.notna(
), 'CenterType'] = address_out.CenterType_jc.dropna()

# Generate hospital keys from AHA hospital list
address_out['HOSP_KEY'] = address_out.index.to_series().apply(
    lambda x: 'K' + colnames.cast_to_int_then_str(x))
# Generate pretty looking ID
# to categorize whether the ID came from A (AHA) or O (JC)
hosp_id_suffix = address_out.Original_ID_Name.apply(lambda x: x[0])
address_out['HOSP_ID'] = address_out.HOSP_ID.apply(
    lambda x: 'ID' + colnames.cast_to_int_then_str(x)) + hosp_id_suffix
hosp_keys = address_out[[
    'HOSP_KEY', 'HOSP_ID', 'Source', 'Original_ID_Name', 'OrganizationId',
    'AHA_ID'
]]

# Saving results
hosp_keys.to_csv(data_io.PROCESSED_DATA / 'hospital_keys_master_v2.csv',
                 index=False)
address_out[OUTPUT_COLS_ORDER].to_csv(data_io.PROCESSED_DATA /
                                      'hospital_address_master_v2.csv',
                                      index=False)

# # Google maps Address searching
# import maps
# JC_searched_filedir = data_io.PROCESSED_DATA / 'jc_aha_manual_searched.csv'
#
# if JC_searched_filedir.exists():
#     jc_for_search = pd.read_csv(JC_searched_filedir)
# else:
#     jc_cols_for_search = [
#         'HOSP_ID_x', 'Hospital Name_x', 'City', 'State', 'Zipcode_x',
#         'Source_x', 'Original_ID_Name_x'
#     ]
#     jc_for_search = jc_aha[jc_cols_for_search].drop_duplicates().reset_index(drop=True)
#
#     # add cols to store google maps data
#     G_cols = [
#         'G_Name', 'G_Address', 'G_Latitude', 'G_Longitude', 'G_Failed_Lookup'
#     ]
#     for gc in G_cols:
#         jc_for_search[gc] = np.nan
#     client = maps.get_client()
#     for idx, row in jc_for_search.iterrows():
#         if pd.notna(row['G_Failed_Lookup']): continue
#         name = row['Hospital Name_x']
#         city = row['City']
#         state = row['State']
#         postal = row['Zipcode_x']
#         searchterm = ' '.join([name, city, state, postal])
#         results = maps.get_hospital_location(searchterm, client)
#         if not results:
#             jc_for_search.loc[idx, 'G_Failed_Lookup'] = True
#             print(f"Found no results for {idx}: {searchterm}")
#         else:
#             jc_for_search.loc[idx, 'G_Address'] = results['Address']
#             jc_for_search.loc[idx, 'G_Name'] = results['Name']
#             jc_for_search.loc[idx, 'G_Latitude'] = results['Latitude']
#             jc_for_search.loc[idx, 'G_Longitude'] = results['Longitude']
#             jc_for_search.loc[idx, 'G_Failed_Lookup'] = False
#     jc_for_search.to_csv(JC_searched_filedir, index=False)
#
# address_parsed = jc_for_search['G_Address'].apply(
#     lambda x: [f.strip() for f in x.split(',')]
#     if isinstance(x, str) else np.nan)
# # cleaning
# address_parsed.dropna(inplace=True)
# # fix special cases, need to do manually every run
# address_parsed[address_parsed.apply(lambda x: len(x) != 4)]
# address_parsed[12] = address_parsed[12][1:]
# address_parsed[63] = [''] + address_parsed[63]
# address_parsed[address_parsed.apply(lambda x: len(x) != 4)]
#
# jc_address = pd.DataFrame(list(address_parsed),
#                           columns=['Address', 'City', 'StateZip', 'Country'],
#                           index=address_parsed.index)
# zip_state_jc_address = pd.DataFrame(list(
#     jc_address['StateZip'].str.split(' ')),
#                                     columns=['State', 'Zip'],
#                                     index=jc_address.index)
# jc_address = jc_address.join(zip_state_jc_address)
# jc_address.drop('StateZip', axis=1, inplace=True)
#
# jc_searched = jc_for_search.join(jc_address['Address'])
# jc_searched = jc_searched.rename({'Address': 'Address_Searched'}, axis=1)
#
# jc_aha = jc_aha.merge(jc_searched[['HOSP_ID_x', 'Address_Searched']],
#                       on='HOSP_ID_x',
#                       how='left')
# jc_aha = jc_aha.drop('Address_x',
#                      axis=1).rename({'Address_Searched': 'Address_x'}, axis=1)
#
# GENERIC_HOSP_WORDS = [
#     'the', 'system', 'hospital', 'center', 'medical', 'health', 'university',
#     'care'
# ]
#
#
# def name_comparison(df, generic_filter=True, mode='intersect'):
#     hosp_x = set(df['Hospital Name_x'].lower().split(' '))
#     hosp_y = set(df['Hospital Name_y'].lower().split(' '))
#     if generic_filter:
#         # print('generic filter on')
#         for word in GENERIC_HOSP_WORDS:
#             if word in hosp_x: hosp_x.remove(word)
#             if word in hosp_y: hosp_y.remove(word)
#     if mode == 'intersect':
#         return len(hosp_x.intersection(hosp_y))
#     else:
#         return len(hosp_x - hosp_y) + len(hosp_y - hosp_x)
#
#
# STREET_TYPE_WORDS = [
#     'ave', 'avenue', 'st', 'dr', 'pl', 'way', 'blvd', 'rd', 'street', 'drive',
#     'boulevard', 'road', 'turnpike'
# ]
#
#
# def address_comparison(df, street_type_filter=True, mode='intersect'):
#     if df[['Address_x', 'Address_y']].isna().any(): return 0
#     hosp_x = set(df['Address_x'].replace(',', '').lower().split(' '))
#     hosp_y = set(df['Address_y'].replace(',', '').lower().split(' '))
#     if street_type_filter:
#         # print('generic filter on')
#         for word in STREET_TYPE_WORDS:
#             if word in hosp_x: hosp_x.remove(word)
#             if word in hosp_y: hosp_y.remove(word)
#     if mode == 'intersect':
#         return len(hosp_x.intersection(hosp_y))
#     else:
#         return len(hosp_x - hosp_y) + len(hosp_y - hosp_x)
#
#
# # Compare hospital name and address to find true matches
# num_shared_words = jc_aha.apply(name_comparison, axis=1)
# # name need to share at least one word that is not generic
# jc_aha2 = jc_aha[(num_shared_words > 0)]
# # match by  with hosp name sharing highest number of common words
# jc_aha2['_num_shared_words'] = jc_aha2.apply(name_comparison,
#                                              axis=1,
#                                              generic_filter=False)
# # groupby each JC hospital and take the row w most similar name
# intersect_mask = jc_aha2.groupby(
#     'Hospital Name_x', as_index=False)['_num_shared_words'].transform(
#         'max')['_num_shared_words'] == jc_aha2['_num_shared_words']
# jc_aha2 = jc_aha2[intersect_mask]
#
# # choose one where address share most similarity as well
# jc_aha2['_num_shared_address_words'] = jc_aha2.apply(address_comparison,
#                                                      axis=1)
# intersect_mask = jc_aha2.groupby(
#     'Hospital Name_x',
#     as_index=False)['_num_shared_address_words'].transform('max')[
#         '_num_shared_address_words'] == jc_aha2['_num_shared_address_words']
# jc_aha2 = jc_aha2[intersect_mask]
#
# jc_aha_shared = jc_aha2
# # remove generic footer in JC hospital name
# jc_aha_shared['Hospital Name_x'] = jc_aha_shared[
#     'Hospital Name_x'].str.replace(', LCC', '').str.replace(', Inc.', '')
# # find # different words between JC hospital name and AHA hospital name
# jc_aha_shared['_num_non_shared_words'] = jc_aha_shared.apply(
#     name_comparison, axis=1, generic_filter=True, mode='difference')
# # take the row with least difference in # of words
# not_intersect_mask = jc_aha_shared.groupby([
#     'Hospital Name_x'
# ], as_index=False)['_num_non_shared_words'].transform(
#     'min')['_num_non_shared_words'] == jc_aha_shared['_num_non_shared_words']
# jc_aha_shared = jc_aha_shared[not_intersect_mask]
#
# # preview shared matches results
# jc_aha_shared.to_csv(data_io.output / 'jc_aha_shared.csv')
#
# # manual check
# jc_aha_shared.shape
# hosp_id_count = jc_aha_shared.groupby('HOSP_ID_x').agg({'HOSP_ID_x': 'count'})
# hosp_id_problem = hosp_id_count.index[list(
#     hosp_id_count['HOSP_ID_x'] > 1)]  # should be empty
# hosp_id_problem
