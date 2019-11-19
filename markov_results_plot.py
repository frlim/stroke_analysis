import data_io
import pandas as pd
import matplotlib.pyplot as plt
import parameters as param

upper = 1
for time_since_symptoms in range(param.SYMP_MIN, param.SYMP_MAX + upper, 10):
    for race in range(param.RACE_MIN, param.RACE_MAX + upper):
        agg_markov_name = data_io.BASIC_ANALYSIS_OUTPUT / param.build_filename_prefix(
            time_since_symptoms=time_since_symptoms,
            race=race,
            suffix='_aggregated_markov_changes',
            format='.xlsx')
        print(agg_markov_name)
        agg_markov = pd.read_excel(agg_markov_name)
        if race == param.RACE_MIN:
            agg_markov_total = agg_markov
        else:
            agg_markov_total = agg_markov_total.append(agg_markov)

    dplot_large = {}
    dplot = {}
    for idx, loc in agg_markov_total.Location.iteritems():
        a, b = agg_markov_total.loc[
            idx, 'RACE'], agg_markov_total.loc[idx, 'QALYdiff_af'] * 365
        dplot[loc] = (a, b)
        if (b > 70).any(): dplot_large[loc] = (a, b)

    fig, ax = plt.subplots()
    for loc, (race, qaly_day_diff) in dplot.items():
        plt.plot(race, qaly_day_diff, '.-', label=loc)
    plt.xticks(range(0, 10))
    plt.xlabel('RACE score')
    plt.ylabel(
        'Quality-adjusted days gained from\n Going to Hospital B instead of Hospital A'
    )
    # plt.suptitle('Patiet Outcome when using Real Hospital DTN data')
    plt.title(
        'Cases where revised model chooses Hospital B\n and generic model chooses hospital A'
    )
    plt.ylim((0, 80))
    # fig.subplots_adjust(bottom=.12)
    # plt.tight_layout()
    plt.legend(bbox_to_anchor=(1.4,1),loc='upper right', ncol=2)
    outname = data_io.GRAPH_OUTPUT / param.build_filename_prefix(
        race='all',
        time_since_symptoms=time_since_symptoms,
        suffix='_QALYdiff_vs_RACE',
        format='.png')
    fig.savefig(outname, dpi=500)

    fig, ax = plt.subplots()
    for loc, (race, qaly_day_diff) in dplot_large.items():
        plt.plot(race, qaly_day_diff, '.-', label=loc)

    plt.xticks(range(0, 10))
    plt.xlabel('RACE score')
    plt.ylabel(
        'Quality-adjusted days gained from\n Going to Hospital B instead of Hospital A'
    )
    # plt.suptitle('Patiet Outcome when using Real Hospital DTN data')
    plt.title(
        'Cases where revised model chooses Hospital B\n and generic model chooses hospital A'
    )
    plt.ylim((0, 80))
    # fig.subplots_adjust(bottom=.12)
    # plt.tight_layout()
    plt.legend(bbox_to_anchor=(1.4,1),loc='upper right', ncol=2)
    outname = data_io.GRAPH_OUTPUT / param.build_filename_prefix(
        race='all',
        time_since_symptoms=time_since_symptoms,
        suffix='_large_QALYdiff_vs_RACE',
        format='.png')
    fig.savefig(outname, dpi=500)
