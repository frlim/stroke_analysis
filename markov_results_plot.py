import data_io
import pandas as pd
from pathlib import Path
import glob
import numpy as np
import matplotlib.pyplot as plt

hospital_path = Path('MA_n=100.csv')
times_path = Path('MA_n=100.csv')
sex_str='male'
age=70
race=7
time_since_symptoms=40
s_default='auto'


AGE_MIN = 65
AGE_MAX = 65
RACE_MIN = 0
RACE_MAX = 9
SYMP_MIN = 10
SYMP_MAX = 100

upper=1
for time_since_symptoms in range(SYMP_MIN,SYMP_MAX+upper,10):
    for race in range(RACE_MIN,RACE_MAX+upper):
        agg_markov_name = f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_aggregated_markov_changes.xlsx'
        print(agg_markov_name)
        agg_markov = pd.read_excel(data_io.ANALYSIS_OUTPUT/agg_markov_name)
        if race == RACE_MIN:
            agg_markov_total = agg_markov
        else:
            agg_markov_total = agg_markov_total.append(agg_markov)

    dplot={}
    for loc in range(0,100):
        loc_m = agg_markov_total["Location"]==loc
        a,b = agg_markov_total.loc[loc_m,'RACE'],agg_markov_total.loc[loc_m,'QALYdiff_af']*365
        if (b>10).any(): dplot[loc] = (a,b)

    fig,ax = plt.subplots()
    for loc,(race,qaly_day_diff) in dplot.items():
        plt.plot(race,qaly_day_diff,'.-',label=f'loc:{loc}')

    plt.xticks(range(0,10))
    plt.xlabel('RACE score')
    plt.ylabel('Quality-adjusted days gained from\n Going to Hospital A instead of Hospital B')
    # plt.suptitle('Patiet Outcome when using Real Hospital DTN data')
    plt.title('Cases where real-data model chooses Hospital A\n and no-real-data model chooses hospital B')
    plt.ylim((0,60))
    # fig.subplots_adjust(bottom=.12)
    plt.tight_layout()
    plt.legend()
    outname =  f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_symptom={time_since_symptoms}_nsim={s_default}_large_QALYdiff_vs_RACE.png'
    outname
    fig.savefig(data_io.GRAPH_OUTPUT/outname,dpi=500)
