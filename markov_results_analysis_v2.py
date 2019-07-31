import data_io
import pandas as pd
from pathlib import Path
import glob
import numpy as np
import re

hospital_path = Path('MA_n=1000.csv')
times_path = Path('MA_n=1000.csv')
sex_str='male'
age=85
race=1
time_since_symptoms=10
s_default=2000
AGE_MIN = 75
AGE_MAX = 75
RACE_MIN = 4
RACE_MAX = 9
SYMP_MIN = 40
SYMP_MAX = 40

def get_target_center(str_input):
    types = [r"Comprehensive to (.+)",r"Primary to (.+)",r"Drip and Ship (.+) to (.+)"]
    for t in types:
        m = re.search(t,str_input)
        if m:
            return m.group(1)

upper=1
for age in range(AGE_MIN,AGE_MAX+upper,5):
    for race in range(RACE_MIN,RACE_MAX+upper):
        for time_since_symptoms in range(SYMP_MIN,SYMP_MAX+upper,10):

            res_name=f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_changed.csv'
            print(res_name)

            basic_res = pd.read_csv(data_io.BASIC_ANALYSIS_OUTPUT/res_name)
            locs = basic_res['Location']
            all_options = basic_res['AllOptions'].str.split(',')
            for idx,loc in locs.iteritems():
                b_markov_res_name = data_io.LOCAL_OUTPUT/f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_loc={loc}_beAHA_detailed_outcome.csv'
                a_markov_res_name = data_io.LOCAL_OUTPUT/f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_loc={loc}_afAHA_detailed_outcome.csv'
                if not (b_markov_res_name.exists() & a_markov_res_name.exists()): continue
                print(b_markov_res_name)

                b_markov_res = pd.read_csv(b_markov_res_name)
                a_markov_res = pd.read_csv(a_markov_res_name)
                b_markov_res = b_markov_res[b_markov_res.Variable=='QALY']
                a_markov_res = a_markov_res[a_markov_res.Variable=='QALY']

                #keep only columns that have info about centers of interest
                b_markov_res_centers = np.array([get_target_center(str(c)) for c in b_markov_res.columns])
                all_truth = (b_markov_res_centers == basic_res.loc[idx,'BestCenter_be']) | (b_markov_res_centers == basic_res.loc[idx,'BestCenter_af'])
                b_markov_res = b_markov_res.loc[:,all_truth]
                a_markov_res_centers = np.array([get_target_center(str(c)) for c in a_markov_res.columns])
                all_truth = (a_markov_res_centers == basic_res.loc[idx,'BestCenter_be']) | (a_markov_res_centers == basic_res.loc[idx,'BestCenter_af'])
                a_markov_res = a_markov_res.loc[:,all_truth]

                b_agg = b_markov_res.agg({'describe'})
                a_agg = a_markov_res.agg({'describe'})
                b_strategies = b_agg.columns.get_level_values(0)
                a_strategies = a_agg.columns.get_level_values(0)
                a_agg.columns = a_strategies
                b_agg.columns = b_strategies


                col_names = ['version','strategy']
                out = pd.concat([b_agg,a_agg],axis=1,keys=['beAHA','afAHA'],names=col_names).swaplevel(axis=1)
                out.sort_index(axis=1,inplace=True)
                out = pd.concat([out],keys=[str(loc)],names=['location'])
                out.to_excel(data_io.MARKOV_ANALYSIS_OUTPUT/f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_loc={loc}_markov_comparison.xlsx')
