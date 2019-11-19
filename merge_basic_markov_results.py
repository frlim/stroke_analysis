import data_io
import pandas as pd
import numpy as np
import re
import parameters as param

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
            bests_be = basic_res['BestCenter_be']
            bests_af = basic_res['BestCenter_af']
            all_options = basic_res['AllOptions'].str.split(',')
            basic_res.set_index("Location", inplace=True)

            for idx, loc in locs.iteritems():
                markov_comparison_name = data_io.MARKOV_ANALYSIS_OUTPUT / param.build_filename_wlocation_prefix(
                    age=age,
                    race=race,
                    time_since_symptoms=time_since_symptoms,
                    loc=loc,
                    suffix='_markov_comparison',
                    format='.xlsx')
                markov_comparison = pd.read_excel(markov_comparison_name,
                                                  index_col=[0, 1],
                                                  header=[0, 1])
                print(markov_comparison_name)

                def get_target_center(str_input):
                    types = [
                        r"Comprehensive to (.+)", r"Primary to (.+)",
                        r"Drip and Ship (.+) to (.+)"
                    ]
                    for t in types:
                        m = re.search(t, str_input)
                        if m:
                            return m.group(1)

                columns_df = markov_comparison.columns.to_frame()
                new_columns = columns_df.join(columns_df['strategy'].apply(
                    get_target_center).rename('target'))
                multi_columns = pd.MultiIndex.from_frame(new_columns)
                #swap level
                multi_columns = multi_columns.swaplevel(0, 2)
                markov_comparison2 = markov_comparison.copy()
                markov_comparison2.columns = multi_columns

                def max_by_target(group):
                    return group.groupby(level='target').agg(["max", "idxmax"])

                def sort_by_max_desc(group):
                    max_col = np.nonzero(
                        ["max" in col for col in group.columns])[0][0]
                    return group.sort_values(by=group.columns[max_col],
                                             ascending=False)

                def get_col_index(out, col_name="max"):
                    return np.nonzero([col_name in col
                                       for col in out.columns])[0][0]

                def get_row_index(out, idx_name="max"):
                    return np.nonzero([idx_name in row
                                       for row in out.index])[0][0]

                idx = pd.IndexSlice
                version_groups = markov_comparison2.loc[
                    idx[:, "mean"], :].T.groupby(level='version')
                out = version_groups.apply(max_by_target).groupby(
                    level="version", group_keys=False).apply(sort_by_max_desc)
                # keep only strategy name in idxmax column
                out[out.columns[get_col_index(
                    out, "idxmax")]] = out[out.columns[get_col_index(
                        out, "idxmax")]].apply(lambda x: x[2])

                max_col_idx = get_col_index(out)

                diff_col_name = tuple(
                    n if i != 2 else "diff"
                    for i, n in enumerate(out.columns[max_col_idx]))

                diff_col = out[out.columns[max_col_idx]].groupby(
                    level="version").diff(periods=-1).rename(diff_col_name,
                                                             axis=1)
                out2 = out.join(diff_col).T

                out3 = out2.dropna(axis=1)

                basic_res.loc[loc, "QALYdiff_be"] = out3.loc[out3.index[
                    get_row_index(out3, "diff")]]["beAHA"].values
                basic_res.loc[loc, "QALYdiff_af"] = out3.loc[out3.index[
                    get_row_index(out3, "diff")]]["afAHA"].values
                basic_res.loc[loc, "BestStrategy_be"] = out3.loc[out3.index[
                    get_row_index(out3, "idxmax")]]["beAHA"].values
                basic_res.loc[loc, "BestStrategy_af"] = out3.loc[out3.index[
                    get_row_index(out3, "idxmax")]]["afAHA"].values

            basic_res.to_excel(data_io.BASIC_ANALYSIS_OUTPUT /
                               param.build_filename_prefix(
                                   age=age,
                                   race=race,
                                   time_since_symptoms=time_since_symptoms,
                                   suffix='_aggregated_markov_changes',
                                   format='.xlsx'))
