import pandas as pd
import data_io


hosp_address = pd.read_csv(data_io.PROCESSED_DATA /
                           'hospital_address_master_v2.csv',
                           dtype=str)

hosp_address[hosp_address.Source!='Joint Commission'].State.value_counts()
# include states surrounding states we have DTN data for
data_states = ['CT','ME','MA','NH','RI','VT','NJ','NY','DE','MD']
surrounding_states = ['VA','DC','PA','OH','WV']
NE_states = data_states+surrounding_states
NE_hospitals = hosp_address.loc[hosp_address.State.isin(NE_states),:]
NE_hospitals.to_csv(data_io.PROCESSED_DATA /
                           'hospital_address_NE_v2.csv',index=False)
