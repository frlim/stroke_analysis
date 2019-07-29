import pandas as pd
import data_io
import xlwings
import numpy as np
import column_names as cols

dtn = data_io.DTN()

too_long_tpa_m = (dtn[cols.tpa_time_cols] > 270).any(axis=1)
dtn.columns

long_dtn = dtn.loc[too_long_tpa_m, ['HOSP_KEY', 'IVTPA_N'] +
                   cols.tpa_time_cols]
dtn[cols.evt_time_cols].agg({col: 'describe' for col in cols.evt_time_cols})

# look up hospital w long times
hosp_key = data_io.HOSP_KEY()
hosp_addy = data_io.HOSP_ADDY()
hosp_key.merge(long_dtn, on='HOSP_KEY').merge(hosp_addy, on='AHA_ID')

# cap at 270 mins for TPA treatment time
dtn2 = dtn[cols.tpa_time_cols]
dtn2[dtn2 > 270] = 270
dtn2 = dtn2.join(dtn[['HOSP_KEY', 'IVTPA_N']]).join(
    dtn[['ARTPUNC_N'] + cols.evt_time_cols])
dtn2 = dtn2[['HOSP_KEY', 'IVTPA_N'] + cols.tpa_time_cols + ['ARTPUNC_N'] +
            cols.evt_time_cols]
prim_filter = dtn2['ARTPUNC_MEDIAN'].isna()
dtn_hosp_type = prim_filter.map({
    True: 'Primary',
    False: 'Comprehensive'
}).rename('CenterType')
dtn2 = dtn2.join(dtn_hosp_type)

out = dtn2.groupby('CenterType').agg(
    {col: 'describe'
     for col in cols.tpa_time_cols + cols.evt_time_cols})
out.columns.names = ['Treatment_Quantile', 'Statistic']
out.T.to_excel(data_io.output / 'aggregated_hospital_DTN_stats.xlsx')

dtn2.to_excel(
    data_io.PROCESSED_DATA / 'deidentified_DTN_cap270tpa.xlsx', index=False)
