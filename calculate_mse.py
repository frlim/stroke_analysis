import data_io
import pandas as pd

filename = 'times=MA_n=100_hospitals=MA_n=100_male_before_AHAdata.csv'
before_df = pd.read_csv(data_io.MODELOUT_PATH/filename)
before_df
filename = 'times=MA_n=100_hospitals=MA_n=100_male_after_AHAdata.csv'
after_df = pd.read_csv(data_io.MODELOUT_PATH/filename)
after_df

# Pair each row together through merge
# to ensure we're comparing the same scenario
merge = before_df.merge(after_df,on=['Location','Patient','Sex','Age','Symptoms','RACE','PSC Count','CSC Count'],how='outer',suffixes=('_b','_a'))


# Get only count columns, discard input variable cols
NON_COUNT_COLS = ['Location','Patient','Varying Hospitals','PSC Count','CSC Count',
    'Sex','Age','Symptoms','RACE']
count_cols = [ not any(col.find(name) >-1 for name in NON_COUNT_COLS) for col in merge.columns]
merge_counts = merge.loc[:,count_cols]

# Split into before and after dfs
b_cols = [c[-2:]=='_b' for c in merge_counts.columns]
a_cols = [c[-2:]=='_a' for c in merge_counts.columns]
before_counts = merge_counts.loc[:,b_cols]
after_counts = merge_counts.loc[:,a_cols]


# Rearrage columns of after df to match that of before df
# Get rid of column suffixes
before_counts.columns = [c[:-2] for c in before_counts.columns]
after_counts.columns = [c[:-2] for c in after_counts.columns]
after_counts = after_counts.loc[:,before_counts.columns] # rearrange
after_counts.columns
#mean square error
num_hospitals = merge['PSC Count']+merge['CSC Count']
#num of hospital that were a possible choice for each scenario
mse_counts = (before_counts-after_counts).pow(2).sum(axis=1)/num_hospitals
mse_counts.describe()


mse_counts

mse_counts
