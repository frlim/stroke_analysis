import xlwings as xw
import data_io
import pandas as pd
def _load_dtn_file(dtn_file, cell_range='A1:M275'):
    sheet = xw.Book(str(dtn_file)).sheets[0]
    return sheet[cell_range].options(
        convert=pd.DataFrame, index=False, header=True).value

data_io.DTN_PATH/'deidentified_DTN.xlsx'
dtn_df = _load_dtn_file(data_io.DTN_PATH/'deidentified_DTN.xlsx')

dtn_df['IVTPA_MEDIAN'].describe()

dtn_df.loc[dtn_df['IVTPA_MEDIAN']>120,:]
