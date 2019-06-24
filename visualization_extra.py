'''Generate visualizations of points and hospitals'''
import os
import argparse
import pandas as pd
from gmplot import gmplot
import hospitals
import maps
import tools
import visualization
from pathlib import Path
import xlwings as xw
import random


# get latitude and longitude for each patient location, identifiable by loc ID
# method 1
stroke_data_path = Path('Z:\\stroke_data')
points = pd.read_csv('data/points/MA_n=100.csv')
points.index.name = 'ID'
points.reset_index(inplace=True)
# method 2 if we already having data
gmap_path = Path('output/maps')
points_fname = 'sexmale_age70.0_race8.0_symptom50.0_points_colors.csv'
points = pd.read_csv(gmap_path/points_fname)


# get output of stroke_model
output_path = Path('C:\\Users\\hqt2102\\OneDrive - cumc.columbia.edu\\Stroke\\patrick_stroke\\output')
out_fname = 'times=MA_n=100_hospitals=MA_n=100_male_before_AHAdata.csv'
model_output = pd.read_csv(output_path/out_fname)
useAHA = False


# identify center lat and longitude by HOSP_KEY
hosp = pd.read_csv(stroke_data_path/'inner_join_siteID.csv',sep='|')

sheet = xw.Book(str(stroke_data_path/'hospital_keys.xlsx') ).sheets[0]
hosp_key = sheet['A1:C275'].options(convert=pd.DataFrame,index=False,header=True).value
centers = hosp.merge(hosp_key,on='AHA_ID',how='left',indicator=True)

centers.columns
centers.Latitude
# run visualize.create_map() to draw green dots and blue,red markers
# group model output by patient profiles
output_groups = model_output.groupby(['Sex','Age','Symptoms','RACE'])
#put group into a list of dfs
output_groups_list = [df for g_name,df in output_groups]
group=output_groups_list[0]
html_name = f'sex{group.Sex.iloc[0]}_age{group.Age.iloc[0]}_race{group.RACE.iloc[0]}_symptom{group.Symptoms.iloc[0]}'
if useAHA:
    html_name += 'afterAHA'
else:
    html_name += 'beforeAHA'
gmap=visualization.create_map(points,centers,name=html_name,heatmap=False)


MAX_THICKNESS=20

generate_color = 'GMapColor' not in points.columns
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
    for c_id,weight in center_weights.iteritems():
        mask = centers['HOSP_KEY']==c_id
        c_lat,c_long = centers.loc[mask,'Latitude'].iloc[0],centers.loc[mask,'Longitude'].iloc[0]
        # print(f'Center Coordinates:{c_lat,c_long} Count:{weight}')
        line_thickness = MAX_THICKNESS*weight
        gmap.plot((p_lat,c_lat),(p_long,c_long),color=color,edge_width=line_thickness)

# Save color
if generate_color: points.to_csv(f'output/maps/{html_name}_points_colors.csv',index=False)
gmap.draw(os.path.join(visualization.MAP_DIR, f'{html_name}.html'))
