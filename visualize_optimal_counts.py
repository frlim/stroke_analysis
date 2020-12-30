import data_io
import pandas as pd
from pathlib import Path
import parameters as param
import plotly.graph_objects as go
import plotly.offline as py
import json
import re
import argparse

#stroke_locations_data_path = Path('/Users/Ryan/Stroke_scripts/stroke_locations/data')
stroke_locations_data_path = Path('/Volumes/dom_dgm_hur$/stroke_data/model_data/stroke_location/data')
fname = Path('NY_MA_NJ_CT_NH_RI_ME_VT_n=10000.csv') # latitude/longitude for all 1000 locations
model_output_path = Path('/Users/francescalim/Desktop/stroke_model/outputs/stroke_output_pid_250') # input files
print(f'Reading output from {model_output_path}')
points_p=stroke_locations_data_path/'points'/fname
hospitals_p=data_io.DTN_PATH /'hospital_address_NE_for_stroke_locations.csv',

MAPBOX_TOKEN = json.loads(open('config/mapbox.json').readline())['token']
addy_path = data_io.DTN_PATH / f'hospital_address_NE_for_stroke_locations.csv' # hospital type, lat/long, transfer_time
key_path = data_io.DTN_PATH / f'hospital_keys_master_v2.csv' # match hospital key (K1) to hospital id in addy_path

def get_hospital_addy_and_keys():
    addy = pd.read_csv(addy_path, sep='|')
    keys = pd.read_csv(key_path, index_col=[1])
    addy['HOSP_KEY'] = addy.HOSP_ID.map(keys.HOSP_KEY.to_dict())
    addy['MAPBOX_NAME'] = addy.HOSP_KEY + ' ' + addy.OrganizationName
    addy['MAPBOX_TYPE'] = addy.CenterType.map({'Comprehensive': 1, 'Primary': 0})
    addy = addy.set_index('HOSP_KEY')
    return addy,keys

_is_a_center = lambda x: re.match('K\d+ [(](CSC|PSC)[)]',x) is not None
_remove_center_type = lambda x: re.sub('[(](CSC|PSC)[)]','',x).strip()

def read_outcome_file(pid,version,model_output_path=model_output_path):
    # Figure out file available to read
    model_fnames = list(model_output_path.glob('*pid={}*{}.csv'.format(pid,version)))
    # print([x.stem[-10:] for x in model_fnames])
    # Get right file based on input args
    model_fname = model_fnames[0]
    print(model_fname.stem)
    optimal_counts = pd.read_csv(model_output_path/model_fname,index_col='Location') # non aggregated outcome
    # drop patient profile columns
    center_cols = optimal_counts.columns[ [_is_a_center(c) for c in optimal_counts.columns]]
    optimal_counts = optimal_counts[center_cols]
    # remove CenterType from hospital columns
    optimal_counts.columns = optimal_counts.columns.map(_remove_center_type)
    return optimal_counts

def plot(lat,lon,addy,count_by_centers,plotpath):

    # remove centers that are nan or 0 count
    # print(count_by_centers)
    count_by_centers = count_by_centers.replace(0,float('nan')).dropna()
    nsim = count_by_centers.sum()

    scatter_list = []

    # plot lines from location to hospitals
    for center_id,count in count_by_centers.iteritems():
        width = int(count/nsim*50)
        if width < 2: continue
        scatter_list.append(
            go.Scattermapbox(lat=[lat,addy.loc[center_id,'Latitude']],
                             lon=[lon,addy.loc[center_id,'Longitude']],
                             mode='lines',
                             name='{:.2f}'.format(count/nsim*100),
                             hoverinfo='text',
                             line=dict(width=width)
                )
        )

    # plot hospital icons
    scatter_list.append(
        go.Scattermapbox(lat=addy.Latitude,
                         lon=addy.Longitude,
                         text=addy.MAPBOX_NAME,
                         hoverinfo='text',
                         mode='markers',
                         name='Center',
                         marker={
                            'color':'gray',
                             'size':
                             13,
                             'symbol':
                             addy.CenterType.map({
                                 'Primary': 'pharmacy',
                                 'Comprehensive': 'marker'
                             })
                         }))

    map_center = {"lat": lat, "lon": lon}

    fig = go.Figure(scatter_list)
    #more mapbox styles
    # https://plot.ly/python/mapbox-layers/
    fig.update_layout(mapbox_style="light",
                      mapbox_accesstoken=MAPBOX_TOKEN,
                      mapbox_zoom=10,
                      mapbox_center=map_center)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(legend=go.layout.Legend(x=0,
                                              y=1,
                                              traceorder="normal",
                                              font=dict(size=12, color="black"),
                                              bgcolor="White",
                                              bordercolor="Blue",
                                              borderwidth=2))

    py.plot(fig, filename=plotpath)

def main(pid=250,version='afAHA',loc_id='L298'):
    points = pd.read_csv(points_p,index_col='LOC_ID')
    lat,lon = points.loc[loc_id,['Latitude','Longitude']].values
    addy,keys = get_hospital_addy_and_keys()
    optimal_counts = read_outcome_file(pid,version)
    count_by_centers = optimal_counts.loc[loc_id]
    plotpath = str(data_io.GRAPH_OUTPUT/f'pid={pid}_loc={loc_id}_{version}.html')
    plot(lat,lon,addy,count_by_centers,plotpath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', help='Patient ID, ex. 0, 1, 2')
    parser.add_argument('version', help='model version: either afAHA or beAHA')
    parser.add_argument('loc_id', help='Location ID, ex. L298')
    args = parser.parse_args()
    print(vars(args))
    main(**vars(args))

# INPUT: visualize_optimal_counts.py 250 afAHA L1
