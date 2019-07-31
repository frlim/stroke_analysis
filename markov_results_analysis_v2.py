import data_io
import pandas as pd
import numpy as np
import re
import parameters as param


def get_target_center(str_input):
    types = [
        r"Comprehensive to (.+)", r"Primary to (.+)",
        r"Drip and Ship (.+) to (.+)"
    ]
    for t in types:
        m = re.search(t, str_input)
        if m:
            return m.group(1)


upper = 1
for age in range(param.AGE_MIN, param.AGE_MAX + upper, 5):
    for race in range(param.RACE_MIN, param.RACE_MAX + upper):
        for time_since_symptoms in range(param.SYMP_MIN,
                                         param.SYMP_MAX + upper, 10):
            res_name = data_io.BASIC_ANALYSIS_OUTPUT / param.build_filename_prefix(
                age=age,
                race=race,
                time_since_symptoms=time_since_symptoms,
                suffix='_changed')
            print(res_name)
            basic_res = pd.read_csv(res_name)
            locs = basic_res['Location']
            all_options = basic_res['AllOptions'].str.split(',')
            for idx, loc in locs.iteritems():
                b_markov_res_name = data_io.LOCAL_OUTPUT / param.build_filename_wlocation_prefix(
                    age=age,
                    race=race,
                    time_since_symptoms=time_since_symptoms,
                    loc=loc,
                    suffix='_beAHA_detailed_outcome')
                a_markov_res_name = data_io.LOCAL_OUTPUT / param.build_filename_wlocation_prefix(
                    age=age,
                    race=race,
                    time_since_symptoms=time_since_symptoms,
                    loc=loc,
                    suffix='_afAHA_detailed_outcome')
                print(b_markov_res_name)

                b_markov_res = pd.read_csv(b_markov_res_name)
                a_markov_res = pd.read_csv(a_markov_res_name)
                b_markov_res = b_markov_res[b_markov_res.Variable == 'QALY']
                a_markov_res = a_markov_res[a_markov_res.Variable == 'QALY']

                #keep only columns that have info about centers of interest
                b_markov_res_centers = np.array(
                    [get_target_center(str(c)) for c in b_markov_res.columns])
                all_truth = (
                    b_markov_res_centers == basic_res.loc[idx, 'BestCenter_be']
                ) | (b_markov_res_centers ==
                     basic_res.loc[idx, 'BestCenter_af'])
                b_markov_res = b_markov_res.loc[:, all_truth]
                a_markov_res_centers = np.array(
                    [get_target_center(str(c)) for c in a_markov_res.columns])
                all_truth = (
                    a_markov_res_centers == basic_res.loc[idx, 'BestCenter_be']
                ) | (a_markov_res_centers ==
                     basic_res.loc[idx, 'BestCenter_af'])
                a_markov_res = a_markov_res.loc[:, all_truth]

                b_agg = b_markov_res.agg({'describe'})
                a_agg = a_markov_res.agg({'describe'})
                b_strategies = b_agg.columns.get_level_values(0)
                a_strategies = a_agg.columns.get_level_values(0)
                a_agg.columns = a_strategies
                b_agg.columns = b_strategies

                col_names = ['version', 'strategy']
                out = pd.concat([b_agg, a_agg],
                                axis=1,
                                keys=['beAHA', 'afAHA'],
                                names=col_names).swaplevel(axis=1)
                out.sort_index(axis=1, inplace=True)
                out = pd.concat([out], keys=[str(loc)], names=['location'])
                out.to_excel(data_io.MARKOV_ANALYSIS_OUTPUT /
                             param.build_filename_wlocation_prefix(
                                 age=age,
                                 race=race,
                                 time_since_symptoms=time_since_symptoms,
                                 loc=loc,
                                 suffix='_markov_comparison',
                                 format='.xlsx'))
