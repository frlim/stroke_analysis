import data_io
import pandas as pd
import parameters as param

# See files that are downloaded
# out = glob.glob(str(data_io.LOCAL_OUTPUT/
# f'times={times_path.stem}_hospitals={hospital_path.stem}_sex=*_age=*_race=*_symptom=*_nsim=*_*AHA.csv'))
# np.sort(out)


def get_basic_results(res_name):

    res = pd.read_csv(res_name)
    center_cols = res.columns[9:]
    res['BestCenter'] = res[center_cols].idxmax(axis=1)
    res['BestCenterType'] = res['BestCenter'].apply(lambda x: 1 if x.split(' ')
                                                    [1] == '(CSC)' else 0)
    res['BestCenterKey'] = res['BestCenter'].apply(lambda x: x.split(' ')[0])
    return res, center_cols


upper = 1
for age in range(param.AGE_MIN, param.AGE_MAX + upper, 5):
    for race in range(param.RACE_MIN, param.RACE_MAX + upper):
        for time_since_symptoms in range(param.SYMP_MIN,
                                         param.SYMP_MAX + upper, 10):
            res_name = data_io.LOCAL_OUTPUT / param.build_filename_prefix(
                age=age,
                race=race,
                time_since_symptoms=time_since_symptoms,
                suffix='_afAHA')
            print(res_name)
            a_res, center_cols = get_basic_results(res_name)
            res_name = data_io.LOCAL_OUTPUT / param.build_filename_prefix(
                age=age,
                race=race,
                time_since_symptoms=time_since_symptoms,
                suffix='_beAHA')
            b_res, center_cols = get_basic_results(res_name)

            input_cols = list(a_res.columns[:9])
            input_cols.pop(input_cols.index('Varying Hospitals'))
            best_option_cols = list(a_res.columns[-3:])
            b_input_cols = b_res.columns[:9]
            ab_res = b_res[input_cols + best_option_cols].merge(
                a_res[input_cols + best_option_cols],
                on=input_cols,
                suffixes=('_be', '_af'))
            # get list of all possible hospitals to go to, (where cell value is not nan)
            ab_res = ab_res.join(
                pd.DataFrame.from_dict({
                    idx: ','.join(center_cols[row.notna()])
                    for idx, row in b_res[center_cols].iterrows()
                },
                                       orient='index',
                                       columns=['AllOptions']))
            center_type_diff = ab_res['BestCenterType_be'] - ab_res[
                'BestCenterType_af']
            # changed_m = center_type_diff != 0
            ab_res.to_csv(
                data_io.BASIC_ANALYSIS_OUTPUT / res_name.stem.replace(
                    'beAHA', 'beaf_best_option.csv'),
                index=False)

            # get changes
            res_name = data_io.BASIC_ANALYSIS_OUTPUT / param.build_filename_prefix(
                age=age,
                race=race,
                time_since_symptoms=time_since_symptoms,
                suffix='_beaf_best_option')
            print(res_name)
            res = pd.read_csv(res_name)
            changed_m = res['BestCenterKey_be'] != res['BestCenterKey_af']
            # changed_m = center_type_diff != 0
            res[changed_m].to_csv(
                data_io.BASIC_ANALYSIS_OUTPUT / param.build_filename_prefix(
                    age=age,
                    race=race,
                    time_since_symptoms=time_since_symptoms,
                    suffix='_changed'),
                index=False)
