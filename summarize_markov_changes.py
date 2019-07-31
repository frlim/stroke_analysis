import pandas as pd
from pathlib import Path
import data_io

hospital_path = Path('MA_n=100.csv')
times_path = Path('MA_n=100.csv')
sex_str='male'
age=75
race=1
time_since_symptoms=40
s_default='auto'
AGE_MIN = 65
AGE_MAX = 85
RACE_MIN = 0
RACE_MAX = 9
SYMP_MIN = 10
SYMP_MAX = 100


agg_markov_name = f'times={times_path.stem}_hospitals={hospital_path.stem}_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}_nsim={s_default}_aggregated_markov_changes.xlsx'
print(agg_markov_name)
agg_markov = pd.read_excel(data_io.ANALYSIS_OUTPUT/agg_markov_name)
agg_markov['QALYdiff_af']*365 > 10
agg_markov.head()

# -1 == PSC -> CSC
# 1 == CSC -> PSC
# 0 == same type change
agg_markov['ChangeType']=(agg_markov['BestCenterType_be']-agg_markov['BestCenterType_af']).map({-1:'PSC to CSC',1:'CSC to PSC',0:'Same Type'})

agg_markov['ChangeType'].value_counts()
agg_markov.groupby('ChangeType').agg({'QALYdiff_af':'describe','QALYdiff_be':'describe'})
