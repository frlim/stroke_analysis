from pathlib import Path
HOSPITALS_PATH = Path('MA_n=1000.csv')
TIMES_PATH = Path('MA_n=1000.csv')
sex_str = 'male'
age = 75
race = 1
time_since_symptoms = 40
s_default = 2000
AGE_MIN = 75
AGE_MAX = 75
RACE_MIN = 0
RACE_MAX = 9
SYMP_MIN = 40
SYMP_MAX = 40


def build_filename_prefix(times_path=TIMES_PATH,
                          hospital_path=HOSPITALS_PATH,
                          sex_str=sex_str,
                          age=age,
                          race=race,
                          time_since_symptoms=time_since_symptoms,
                          s_default=s_default,
                          suffix="",
                          format='.csv'):
    out_str = f'times={times_path.stem}_hospitals={hospital_path.stem}'
    out_str += f'_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}'
    out_str += f'_nsim={s_default}{suffix}{format}'
    return out_str


def build_filename_wlocation_prefix(times_path=TIMES_PATH,
                                    hospital_path=HOSPITALS_PATH,
                                    sex_str=sex_str,
                                    age=age,
                                    race=race,
                                    time_since_symptoms=time_since_symptoms,
                                    s_default=s_default,
                                    loc='L0',
                                    suffix="",
                                    format='.csv'):
    out_str = f'times={times_path.stem}_hospitals={hospital_path.stem}'
    out_str += f'_sex={sex_str}_age={age}_race={race}_symptom={time_since_symptoms}'
    out_str += f'_nsim={s_default}_loc={loc}{suffix}{format}'
    return out_str
