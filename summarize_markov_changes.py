import pandas as pd
from pathlib import Path
import data_io
import parameters as param

dflist=[]
for race in range(param.RACE_MIN,param.RACE_MAX+1):
    agg_markov_name = data_io.BASIC_ANALYSIS_OUTPUT / param.build_filename_prefix(
        race=race, suffix='_aggregated_markov_changes', format='.xlsx')

    agg_markov = pd.read_excel(agg_markov_name)


    def extract_type(val):
        return val.split(' ')[1].replace('(', '').replace(')', '')


    def change_type(df):
        return extract_type(df.BestCenter_be) + ' to ' + extract_type(
            df.BestCenter_af)


    agg_markov['ChangeType'] = agg_markov.apply(change_type, axis=1)

    agg_markov['ChangeType'].value_counts()
    agg_markov['ChangeType'].value_counts().sum()

    agg_gb = agg_markov.groupby('ChangeType').agg({
        'QALYdiff_af': 'describe',
        'QALYdiff_be': 'describe'
    })

    a=agg_markov.agg({
        'QALYdiff_af': 'describe',
        'QALYdiff_be': 'describe'
    })
    agg_gb.loc['All Changes',:] = a.stack().swaplevel().sort_index()
    agg_gb = pd.concat([agg_gb],keys=[race]*agg_gb.shape[0],names=['RACE_score'])
    dflist.append(agg_gb)

agg_gb_append2 = pd.concat(dflist)*365
idx =pd.IndexSlice
agg_gb_append2.loc[:,idx[:,'count']]=agg_gb_append2.loc[:,idx[:,'count']]/365
agg_gb_append2.to_excel(data_io.BASIC_ANALYSIS_OUTPUT/'agg_by_race_score.xlsx')
