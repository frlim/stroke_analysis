# Takes outputs from the stroke model and creates 2 files:
# - []_changed.csv that shows changes in hospital destination between base and enhanced model and QALYs
# - []_summarized.csv that shows base and enhanced model destinations for each location for a patient

import data_io
import pandas as pd
import parameters as param
import re
import time
from tqdm import tqdm

start_time = time.time()

# See files that are downloaded
# out = glob.glob(str(data_io.LOCAL_OUTPUT/
# f'times={times_path.stem}_hospitals={hospital_path.stem}_sex=*_age=*_race=*_symptom=*_nsim=*_*AHA.csv'))
# np.sort(out)

def get_basic_results(res_name):
    '''Input = summary file for each PID that shows hospitals for each location and number of times each hospital is optimal
       Output = dataframe of best hospital for given PID at each location and all hospital keys and counts'''
    res = pd.read_csv(res_name,index_col='Location')
    center_cols = res.columns[10:] # only columns of hospital keys
    # Returns Best Center Key for each location based on max value
    res['BestCenter'] = res[center_cols].idxmax(axis=1) # idxmax: return index of maximum in each row
    # Extract Center Key and Type from BestCenter column
    res['BestCenterType'] = res['BestCenter'].apply(lambda x: "CSC" if x.split(' ')
                                                    [1] == '(CSC)' else "PSC")
    res['BestCenterKey'] = res['BestCenter'].apply(lambda x: x.split(' ')[0])
    return res, center_cols

BEST_CENTER_COLS = ['BestCenterKey','BestCenterType']

def read_agout(fname):
    return pd.read_csv(fname,header=[0,1],index_col=[0])

def _get_most_ce_strategy(agout):
    '''Looks for the one hospital key that is most cost-effective in the aggregated_outcome.csv'''
    return agout.columns[agout.columns.get_level_values('Strategy').str.find('most C/E')>-1][0][0]

def get_variable_stats_from_aggregated_outcome(agout,var='QALY',strategies=None,suffixes=None):
    if strategies is None:
        # get most cost-effective strategy (one strategy for each file)
        most_ce =  _get_most_ce_strategy(agout)
        for_join = agout.loc[var,most_ce].to_frame().T
        suffixes = ['af']
    # idx = pd.IndexSlice
    stats_df_l = []
    for strategy,suffix in zip(strategies,suffixes):
        stat_for_one_strategy = af_agout.loc[var,strategy].to_frame().T
        stat_for_one_strategy.drop("count",axis=1,inplace=True)
        stat_for_one_strategy.columns = [ '_'.join((c,var,suffix)) for c in stat_for_one_strategy.columns]
        stat_for_one_strategy[f"Strategy_{suffix}"] = strategy.replace('- most C/E','').strip()
        stats_df_l.append(stat_for_one_strategy)
    strategies_stats = pd.concat(stats_df_l,axis=1)
    return strategies_stats

for pid in tqdm(range(250,251)):
    # get after AHA result
    res_name = list(data_io.LOCAL_OUTPUT.glob(f'pid={pid}*_afAHA.csv'))[0]
    a_res, center_cols = get_basic_results(res_name) # res = dataframe w/ best type & keys , center_cols = all possible hospital location columns

    # get before AHA result
    res_name = list(data_io.LOCAL_OUTPUT.glob(f'pid={pid}*_beAHA.csv'))[0]
    b_res, center_cols = get_basic_results(res_name)

    # Dataframe of before and after best center key/type for every location
    ab_res = b_res[BEST_CENTER_COLS].join(a_res[BEST_CENTER_COLS],
                                           rsuffix='_af',lsuffix='_be')

    # center_cols is the same for both be and af AHA
    # get list of all possible hospitals to go to, (where cell value is not nan)
    # ab_res = ab_res.join(
    #     pd.DataFrame.from_dict({
    #         idx: ','.join(center_cols[row.notna()])
    #         for idx, row in b_res[center_cols].iterrows()
    #     },
    #                            orient='index',
    #                            columns=['AllOptions']))
    
    # Output the most hospital location for a patient at each location
    ab_res.to_csv(
        data_io.BASIC_ANALYSIS_OUTPUT / res_name.stem.replace(
            'beAHA', 'summarized.csv'))

    # Get changes between base model and enhanced model
    changed_m = ab_res['BestCenterKey_be'] != ab_res['BestCenterKey_af']
    changed_res = ab_res[changed_m] # dataframe of locations for each patient where there was a change in destination

    qaly_stats_l = []
    if changed_res.shape[0] != 0: # only run if changes exist
        # Iterate throuh each location that had a change in optimal destination
        for loc_id in changed_res.index:
            # Enhanced model
            fname = list(data_io.LOCAL_OUTPUT.glob(f'pid={pid}*loc={loc_id}_afAHA*'))[0]
            af_agout = read_agout(fname) # each individual output file (aggregated_outcome.csv)
            # Get the most cost effective strategy - after (af)
            # Note: most c/e strategy is same as best hospital strategy
            af_most_ce = _get_most_ce_strategy(af_agout)

            # Base model
            fname = list(data_io.LOCAL_OUTPUT.glob(f'pid={pid}*loc={loc_id}_beAHA*'))[0]
            be_agout = read_agout(fname)
            # Get the most cost effective strategy - before (be)
            # Note: most c/e strategy is same as best hospital strategy
            be_most_ce = _get_most_ce_strategy(be_agout)

            # ORIGINAL CODE
            # Note: not working because be site name won't appear in af_agout strategy columns
            # Might happen because hospital treatment time is so long it passes the limit a stroke
            # patient can get treatment
            # af_qaly_stats = get_variable_stats_from_aggregated_outcome(af_agout,'QALY',
            #                    [af_most_ce,be_most_ce.replace('- most C/E','').strip()],
            #                    suffixes=("af","be"))

            # Note: This chunk runs but be columns are all empty
            # if be_most_ce not in af_agout.columns.get_level_values(0):
            #     af_qaly_stats = get_variable_stats_from_aggregated_outcome(af_agout,'QALY',
            #                     strategies=[af_most_ce],
            #                     suffixes=["af"])

            # If strategy name not in af_agout columns, only summarize af QALYs
            # af_agout.columns = all possible hospital destinations for each location
            # Check to see if most cost-effectiveness hospital from base model is also in enhanced model
            if be_most_ce.replace('- most C/E','').strip() in af_agout.columns.get_level_values(0):
                # If base model hospital still an option in enhanced model: get qalys from both
                af_qaly_stats = get_variable_stats_from_aggregated_outcome(af_agout,'QALY',
                                [af_most_ce,be_most_ce.replace('- most C/E','').strip()],
                                suffixes=["af","be"])
            # If optimal destination from base model no longer an option in enhanced model, only enhanced QALYs
            else:
                print("Missing Strategy: ", be_most_ce)
                print("for location ", loc_id, "and patient ", pid)
                af_qaly_stats = get_variable_stats_from_aggregated_outcome(af_agout,'QALY',
                                [af_most_ce],
                                suffixes=["af"])
            
            af_qaly_stats.index=[loc_id] # a dataframe, add index column
            # fname = list(data_io.LOCAL_OUTPUT.glob(f'pid={pid}*loc={loc_id}*beAHA*'))[0]
            # be_qaly_stats = get_variable_stats_from_aggregated_outcome(fname,'QALY')
            # be_qaly_stats.index=[loc_id]
            # qaly_stats = be_qaly_stats.join(af_qaly_stats,lsuffix='_be',rsuffix='_af')
            qaly_stats_l.append(af_qaly_stats)

        # Add qalys to all changed destinations
        changed_res = changed_res.join(pd.concat(qaly_stats_l),how='left')
    
        # Create column for difference in mean QALYs
        # mean_QALY_af - mean_QALY_be
        changed_res['diff_QALY'] = changed_res['mean_QALY_af'] - changed_res['mean_QALY_be']

        # Output
        changed_res.to_csv(
            data_io.BASIC_ANALYSIS_OUTPUT / res_name.stem.replace('beAHA','changed.csv'))


print("Code took", time.time() - start_time, "to run")
