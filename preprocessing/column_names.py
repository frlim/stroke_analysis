import pandas as pd
import numpy as np

evt_time_cols = ['IATPA_P25','IATPA_MEDIAN','IATPA_P75']
tpa_time_cols = ['IVTPA_P75','IVTPA_MEDIAN','IVTPA_P25']

def cast_to_int_then_str(x):
    if pd.isnull(x):
        return np.nan
    elif isinstance(x,str):
        return x
    else:
        return str(int(x))
