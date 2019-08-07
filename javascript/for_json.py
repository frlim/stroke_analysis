import pandas as pd
from pathlib import Path
import random
import xlwings as xw
import json
'''Required input to run'''

state = "MA"
nloc = 1000
s_default = 2000
version = 'afAHA'
# generate random color or use old color
# json color file must exist to use old color
generate_color = True

identified_file_path = Path('Z:\\stroke_data\\processed_data')
hosp_latlong_path = identified_file_path / f'strokecenter_address_{state}_for_stroke_locations.csv'
hosp_key_path = identified_file_path / 'hospital_keys_master.csv'
stroke_location_path = Path(
    'C:\\Users\\hqt2102\\OneDrive - cumc.columbia.edu\\Stroke\\stroke_locations'
)
out_path = Path.cwd() / 'data_js'
data_path = Path('F:\\stroke_model_output\\output_080619')

hospital_path = stroke_location_path / 'output' / 'hospitals' / f'{state}_n={nloc}.csv'
times_path = stroke_location_path / 'output' / 'travel_times' / f'{state}_n={nloc}.csv'
points_path = stroke_location_path / 'data' / 'points' / f'{state}_n={nloc}.csv'
sex_str = 'male'
age = 75
race = 7
time_since_symptoms = 40

AGE_MIN = 75
AGE_MAX = 75
RACE_MIN = 0
RACE_MAX = 9
SYMP_MIN = 40
SYMP_MAX = 40

upper = 1


def black_or_white(r, g, b):
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if luminance > 0.5:
        d = 0
    else:
        d = 255
    return (d, d, d)


def random_color():
    # color = "#"+"%06x" % random.randint(0, 0xFFFFFF)
    ra = lambda: random.randint(0, 255)
    r, g, b = ra(), ra(), ra()
    cr, cg, cb = black_or_white(r, g, b)
    color = '#%02X%02X%02X' % (r, g, b)
    complement_color = '#%02X%02X%02X' % (cr, cg, cb)
    return color, complement_color


# Generate MA_n=1000_centers.json
hospitals_latlong = pd.read_csv(hosp_latlong_path, sep='|')
# hospitals_latlong.to_json(out_path/'MA_hopsitals_latlong.json',orient='records')
hosp_key = pd.read_csv(hosp_key_path)
hosp = pd.read_csv(hospital_path)
centers = hospitals_latlong.merge(
    hosp_key, on='HOSP_ID', how='left', indicator=True).merge(
        hosp, how='left')
centers_for_json = centers[[
    'HOSP_KEY', 'Latitude', 'Longitude', 'CenterType', 'transfer_time',
    'destination_KEY'
]]
centers_for_json.to_json(
    out_path / f'{state}_n={nloc}_centers.js', orient='records')

# identify center lat and longitude by HOSP_KEY
# sheet = xw.Book(str(hosp_key_path)).sheets[0]
# hosp_key = sheet['A1:F1918'].options(
#     convert=pd.DataFrame, index=False, header=True).value

for age in range(AGE_MIN, AGE_MAX + upper, 5):
    for race in range(RACE_MIN, RACE_MAX + upper):
        for time_since_symptoms in range(SYMP_MIN, SYMP_MAX + upper, 10):

            if generate_color:
                points = pd.read_csv(points_path, index_col=0)
            else:
                # points_color = pd.read_csv(stroke_location_path/'output/maps/sexmale_age70.0_race8.0_symptom50.0_points_colors.csv')
                points = pd.read_json(
                    out_path / f'{state}_n={nloc}_points.json',
                    orient='index')

            # get output of stroke_model
            output_path = data_path
            out_fname = f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_{version}.csv'
            model_output = pd.read_csv(output_path / out_fname)
            # group model output by patient profiles
            output_groups = model_output.groupby(
                ['Sex', 'Age', 'Symptoms', 'RACE'])
            #put group into a list of dfs
            output_groups_list = [df for g_name, df in output_groups]
            group = output_groups_list[0]

            out_list = []

            for p_id, row in points.iterrows():
                if generate_color:
                    # color = "#"+"%06x" % random.randint(0, 0xFFFFFF)
                    color, complement_color = random_color()
                    points.loc[
                        p_id,
                        'GMapColor'] = color  # save color for later replotting
                    points.loc[
                        p_id,
                        'GMapComColor'] = complement_color  # save color for later replotting
                else:
                    color = points.loc[p_id, 'GMapColor']
                    complement_color = points.loc[p_id, 'GMapComColor']

                p_lat, p_long = row.Latitude, row.Longitude

                print(f'{p_id} Patient Coordinates {p_lat,p_long}')

                center_counts = group.loc[group.Location ==
                                          p_id, group.columns[9:]].iloc[0]
                center_counts.index = [
                    c_str.split(' ')[0] for c_str in center_counts.index
                ]
                center_counts = center_counts[center_counts >
                                              0]  # remove centers with 0 count
                center_weights = center_counts / center_counts.sum(
                )  # convert to weight
                centers_at_point = []
                for c_id, weight in center_weights.iteritems():
                    mask = centers['HOSP_KEY'] == c_id
                    c_lat, c_long = centers.loc[mask, 'Latitude'].iloc[
                        0], centers.loc[mask, 'Longitude'].iloc[0]
                    # print(f'Center Coordinates:{c_lat,c_long} Count:{weight}')
                    a_center = {"Center": c_id, "Weight": weight}
                    centers_at_point.append(a_center)
                best_center = center_weights.idxmax()
                out_list.append({
                    "Point": {
                        "Location": p_id,
                        "Centers": centers_at_point,
                        "Color": color,
                        "ComColor": complement_color,
                        "BestCenter": best_center
                    }
                })

            if generate_color:
                points.to_json(
                    out_path / f'{state}_n={nloc}_points.json',
                    orient='index')
                generate_color = False

            json_str = json.dumps(out_list)
            file = open(
                out_path /
                f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_{version}.json',
                'w')
            # file.write('createLines(')
            file.write(json_str)
            # file.write(');\n')
            # file.write('highLightLinesPoints();\n')
            # file.write('highLightLinesCenters();')
            file.close()
            generate_color = False
