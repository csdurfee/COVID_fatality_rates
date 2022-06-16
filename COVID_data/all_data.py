import pandas as pd
import numpy as np
import datetime

from .deaths_data import *
from .health_data import *
from .income_data import *
from .political_data import *
from .size_data import *
from .vaccine_data import *

def get_all_corr_series(monthly=True):
    all_series = {}
    death_corrs = get_death_corrs(monthly)
    for (date, corrs) in death_corrs.items():
        for c in corrs.keys():
            if c in ["MONTHLY_PER_CAPITA_DEATH_RATE", "THIS_MONTH_DEATHS"]:
                continue
            elif c in all_series:
                all_series[c].append(corrs[c])
            else:
                all_series[c] = [corrs[c]]
    return all_series


def _all_data_base(config):
    return get_covid_fatality_data(config) \
        .reset_index() \
        .merge(get_county_income_data(config), on=['STATE', 'COUNTY']) \
        .set_index("FIPS") \
        .join(get_vax_data(config)) \
        .join(get_county_health_data(config)) \
        .join(get_size_data(config)) \
        .join(get_political_data(config)) \
        .join(get_additional_measure_data(config)) \
        .join(get_social_vuln_data(config)) \
        .join(get_ranked_data(config))

def get_all_data(config):
    all_data = _all_data_base(config)
    population_measure = all_data['POPULATION']

    ## calculate rates/aggs
    all_data['DENSITY'] = population_measure / all_data['ALAND_SQMI']

    all_data['DEATH_RATE'] = all_data['DEATHS'] / population_measure
    all_data['DEATH_RATE_FIRST_YEAR'] = all_data['DEATHS_FIRST_YEAR'] / population_measure
    all_data['DEATH_RATE_SECOND_YEAR'] = all_data['DEATHS_SECOND_YEAR'] / population_measure
    all_data['DEATH_RATE_ALPHA'] = all_data['DEATHS_ALPHA'] / population_measure
    all_data['DEATH_RATE_DELTA'] = all_data['DEATHS_DELTA'] / population_measure
    all_data['DEATH_RATE_OMICRON'] = all_data['DEATHS_OMICRON'] / population_measure

    ## drop stuff where we have zeroes (eg Utah reporting 0 fatalities at county level)

    return _filter_uninteresting(_drop_zeroes(all_data))

def _drop_zeroes(data):
    return data[data.DEATHS > 0]

def _filter_uninteresting(data):
    UNINTERESTING = [
        'PER_CAPITA_RANK',
        # 'PER_CAPITA', 
        # 'MEDIAN_HOUSEHOLD', # I am just going to use median family
        'HOUSEHOLDS',
        #'POPN', # this has missing data compared to the 'POPULATION' field.
        #'State',
        #'County',
        '# of Ranked Counties (CHR)',
        'HEALTH_OUTCOMES_RANK (CHR)', 
        'HEALTH_OUTCOMES_QUARTILE (CHR)',
        'HEALTH_FACTORS_RANK (CHR)', 
        'HEALTH_FACTORS_QUARTILE (CHR)',
        '2016_repub_votes',
        '2016_total_votes',
    ]
    return data.drop(UNINTERESTING, axis=1)