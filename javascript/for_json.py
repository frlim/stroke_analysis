import pandas as pd
from pathlib import Path
import random
import xlwings as xw
import json

file_path = Path('Z:\\stroke_data\\')

MA_hospitals_latlong= pd.read_csv(file_path/'inner_join_siteID.csv',sep='|')
# MA_hospitals_latlong.to_json(file_path/'MA_hopsitals_latlong.json',orient='records')

points = pd.read_csv('data/points/MA_n=100.csv')
points.index.name='ID'
points.reset_index(inplace=True)
points_color = pd.read_csv('output/maps/sexmale_age70.0_race8.0_symptom50.0_points_colors.csv')
points_color.drop('ID',axis=1,inplace=True)
points_w_color = points.merge(points_color,on=['Latitude','Longitude'])
points_w_color.to_json(file_path/'MA_n=100_points.js',orient='records')

# get output of stroke_model
output_path = Path('C:\\Users\\hqt2102\\OneDrive - cumc.columbia.edu\\Stroke\\patrick_stroke\\output')
out_fname = 'times=MA_n=100_hospitals=MA_n=100_male_after_AHAdata.csv'
model_output = pd.read_csv(output_path/out_fname)
# group model output by patient profiles
output_groups = model_output.groupby(['Sex','Age','Symptoms','RACE'])
#put group into a list of dfs
output_groups_list = [df for g_name,df in output_groups]
group = output_groups_list[0]

# identify center lat and longitude by HOSP_KEY
sheet = xw.Book(str(file_path/'hospital_keys.xlsx') ).sheets[0]
hosp_key = sheet['A1:C275'].options(convert=pd.DataFrame,index=False,header=True).value
centers = MA_hospitals_latlong.merge(hosp_key,on='AHA_ID',how='left',indicator=True)

centers_for_json=centers[['HOSP_KEY','Latitude','Longitude','CenterType','transfer_time','destinationID']]
centers_for_json.to_json(file_path/'MA_n=100_centers.js',orient='records')

points= points_w_color
out_list=[]
generate_color = False

for p_idx,row in points.iterrows():
    if generate_color:
        color = "#"+"%06x" % random.randint(0, 0xFFFFFF)
        points.loc[p_idx,'GMapColor'] = color # save color for later replotting
    else:
        color = points.loc[p_idx,'GMapColor']
    p_lat,p_long = row.Latitude,row.Longitude
    print(f'Patient Coordinates {p_lat,p_long}')
    p_id = row.ID
    center_counts = group.loc[group.Location == p_id,group.columns[9:]].iloc[0]
    center_counts.index = [int(c_str.split(' ')[0]) for c_str in center_counts.index]
    center_counts = center_counts[center_counts>0] # remove centers with 0 count
    center_weights = center_counts/center_counts.sum() # convert to weight
    centers_at_point=[]
    for c_id,weight in center_weights.iteritems():
        mask = centers['HOSP_KEY']==c_id
        c_lat,c_long = centers.loc[mask,'Latitude'].iloc[0],centers.loc[mask,'Longitude'].iloc[0]
        # print(f'Center Coordinates:{c_lat,c_long} Count:{weight}')
        a_center = {"Center":c_id,"Weight":weight}
        centers_at_point.append(a_center)
    out_list.append({"Point":{"Location":row["ID"],"Centers":centers_at_point,"Color":color}})


json.dumps(out_list)
out_dict
pd.DataFrame.from_dict(out_dict)
weight
