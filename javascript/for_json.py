import pandas as pd
from pathlib import Path
import random
import xlwings as xw
import json

'''Required input to run'''

file_path = Path('Z:\\stroke_data\\')
stroke_location_path = Path('C:\\Users\\hqt2102\\OneDrive - cumc.columbia.edu\\Stroke\\stroke_locations')
out_path = Path.cwd()/'data_js'
data_path = Path('E:\\stroke_model_output\\output_070119')
# generate random color or use old color
generate_color = False

hospital_path = Path('MA_n=100.csv')
times_path = Path('MA_n=100.csv')
sex_str='male'
age=80
race=7
time_since_symptoms=40
s_default='auto'
version='beAHA'

AGE_MIN = 65
AGE_MAX = 85
RACE_MIN = 0
RACE_MAX = 9
SYMP_MIN = 10
SYMP_MAX = 100

upper=1
for age in range(AGE_MIN,AGE_MAX+upper,5):
    for race in range(RACE_MIN,RACE_MAX+upper):
        for time_since_symptoms in range(SYMP_MIN,SYMP_MAX+upper,10):

            MA_hospitals_latlong= pd.read_csv(file_path/'inner_join_siteID.csv',sep='|')
            # MA_hospitals_latlong.to_json(file_path/'MA_hopsitals_latlong.json',orient='records')

            if generate_color:
                points = pd.read_csv(stroke_location_path/'data/points/MA_n=100.csv')
                points.index.name='ID'
                points.reset_index(inplace=True)
            else:
                # points_color = pd.read_csv(stroke_location_path/'output/maps/sexmale_age70.0_race8.0_symptom50.0_points_colors.csv')
                points = pd.read_json(out_path/'MA_n=100_points.json',orient='records')


            # get output of stroke_model
            output_path = data_path
            out_fname = f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_{version}.csv'
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
            # centers_for_json.to_json(out_path/'MA_n=100_centers.js',orient='records')

            def black_or_white(r,g,b):
                luminance = ( 0.299 * r + 0.587 * g + 0.114 * b)/255;
                if luminance > 0.5:
                    d =0;
                else:
                    d=255
                return (d,d,d)

            out_list=[]

            for p_idx,row in points.iterrows():
                if generate_color:
                    # color = "#"+"%06x" % random.randint(0, 0xFFFFFF)
                    ra = lambda: random.randint(0,255)
                    r,g,b = ra(),ra(),ra()
                    cr,cg,cb = black_or_white(r,g,b)
                    color = '#%02X%02X%02X'%(r,g,b)
                    complement_color = '#%02X%02X%02X'%(cr,cg,cb)
                    points.loc[p_idx,'GMapColor'] = color # save color for later replotting
                    points.loc[p_idx,'GMapComColor'] = complement_color # save color for later replotting
                else:
                    color = points.loc[p_idx,'GMapColor']
                    complement_color = points.loc[p_idx,'GMapComColor']
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
                    a_center = {"Center":int(c_id),"Weight":weight}
                    centers_at_point.append(a_center)
                best_center = int(center_weights.idxmax())
                out_list.append({"Point":{"Location":row["ID"],"Centers":centers_at_point,"Color":color,
                                "ComColor":complement_color,
                                "BestCenter":best_center}})

            if generate_color:
                points.to_json(out_path/'MA_n=100_points.json',orient='records')
                generate_color=False


            json_str=json.dumps(out_list)
            file = open(out_path/f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_{version}.json','w')
            # file.write('createLines(')
            file.write(json_str)
            # file.write(');\n')
            # file.write('highLightLinesPoints();\n')
            # file.write('highLightLinesCenters();')
            file.close()
            generate_color=False
