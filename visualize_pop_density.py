import data_io
import pandas as pd
import re
from pathlib import Path
import parameters as param
import plotly.graph_objects as go
import plotly.offline as py
import json
import re
from urllib.request import urlopen

#stroke_locations_data_path = Path('/Users/Ryan/Stroke_scripts/stroke_locations/data')
stroke_locations_data_path = Path('/Volumes/dom_dgm_hur$/stroke_data/model_data/stroke_location/data')
fname = Path('NY_MA_NJ_CT_NH_RI_ME_VT_n=10000.csv') # latitude/longitude for all 1000 locations
points = pd.read_csv(stroke_locations_data_path/'points'/fname,index_col='LOC_ID')
chosen_locs = [f'L{i}' for i in range(1000)]
points = points.loc[chosen_locs,:]

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

density = pd.read_csv("data/cleaned_county_pop_density.csv", dtype={"fips": object})

# Create column for is_rural
def is_rural(row):
    if row['pop_density'] < 500:
        return 1
    else:
        return 0

density['is_rural'] = density.apply(lambda row: is_rural(row), axis=1)

# Plot
scatt_points = go.Scattermapbox(lat=points.Latitude,
                 lon=points.Longitude,
                 text=points.index,
                 hoverinfo='text',
                 mode='markers',
                 name='Patient Location',
                 marker=go.scattermapbox.Marker(size=9,
                                                opacity=0.75,
                                                color='rgb(100, 100, 200)'))

choro = go.Choroplethmapbox(geojson=counties, locations=density.fips, z=density.is_rural,
                                    marker_opacity=0.4, marker_line_width=0, colorscale='temps', text=density.county, hoverinfo='text')

# https://nbviewer.jupyter.org/gist/empet/ea0d142fbce46a57288e920bfd737f7a
fig=go.Figure(data=[choro, scatt_points])
fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=6, mapbox_center = {"lat": points.Latitude.mean(), "lon": points.Longitude.mean()})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

py.plot(fig, filename=str(data_io.GRAPH_OUTPUT/'rural_locations.html'))