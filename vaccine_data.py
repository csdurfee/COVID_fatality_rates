import pandas as pd
import numpy as np


USE_CACHE = True

if USE_CACHE:
    VAX_URL           = "vaccinetracking/vacc_data/data_county_current.csv"
    COVID_DEATHS_URL  = "time_series_covid19_deaths_US.csv"
    PER_CAPITA_URL    =  "percapita.html"
    COUNTY_HEALTH_URL = "2021 County Health Rankings Data - v1.xlsx"

else:
    VAX_URL           = "https://github.com/bansallab/vaccinetracking/blob/main/vacc_data/data_county_current.csv"
    COVID_DEATHS_URL  = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
    PER_CAPITA_URL    = "https://en.wikipedia.org/wiki/List_of_United_States_counties_by_per_capita_income"
    COUNTY_HEALTH_URL = "https://www.countyhealthrankings.org/sites/default/files/media/document/2021%20County%20Health%20Rankings%20Data%20-%20v1.xlsx"

def get_vax_data():
    ## this data is from 
    vax_df = pd.read_csv(VAX_URL, parse_dates=['DATE'])

    ## take only county-level data.
    ## rename to make usage of column clear
    vax_df = vax_df[vax_df.GEOFLAG == 'County'].rename(columns={'COUNTY': 'FIPS'})

    ## these are irrelevant
    vax_df = vax_df.drop(['STATE', 'WEEK', 'YEAR'], axis=1)


    partial  = vax_df[vax_df.CASE_TYPE == 'Partial Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    booster  = vax_df[vax_df.CASE_TYPE == 'Booster Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    complete = vax_df[vax_df.CASE_TYPE == 'Complete Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")

    popn_by_fips = vax_df.loc[vax_df.CASE_TYPE == 'Partial Coverage', ['POPN', 'FIPS']
                                ].set_index('FIPS')

    return partial.join(booster).join(complete).join(popn_by_fips)

def get_covid_fatality_data(vax_data):
    deaths_df = pd.read_csv(COVID_DEATHS_URL) # , dtype = death_dtypes)

    ## FIXME: get the last column of the time series rather than '2/28/22' 
    # hardcoded.
    cols = ['FIPS', 'Admin2', 'Province_State', '2/28/22', '3/11/21']

    deaths_cleaned = deaths_df.loc[:, cols].rename(columns={'3/11/21': 'DEATHS_ONEYEAR',
                                                            '2/28/22': 'DEATHS',
                                                            'Admin2': 'COUNTY',
                                                            'Province_State': 'STATE' })

    covid_df = deaths_cleaned.set_index("FIPS").join(vax_data).dropna()

    covid_df["DEATH_RATE"] = covid_df["DEATHS"] / covid_df["POPN"]

    covid_df["DEATH_RATE_ONEYEAR"] = covid_df["DEATHS_ONEYEAR"] / covid_df["POPN"]

    return covid_df


def get_county_income_data():

    conversions = {
                    'Population': int,
                    'Number ofhouseholds': int
                    }

    html_crud = pd.read_html(PER_CAPITA_URL)[2]

    # this will make rows with "-" in them be nan
    html_crud['Rank'] = pd.to_numeric(html_crud['Rank'], errors="coerce")

    html_crud = html_crud.dropna()

    ## deal with dollar signs, y'all
    # taken from: https://stackoverflow.com/questions/32464280/converting-currency-with-to-numbers-in-python-pandas

    dollar_values = ['Per capitaincome', 'Medianhouseholdincome', 'Medianfamilyincome']


    for v in dollar_values:
        html_crud[v] = html_crud[v].str.replace(r"[$,]", "", regex=True).astype(int)

    html_crud = html_crud.dropna()

    html_crud = html_crud.rename(columns = {
                                    'County or county-equivalent': 'COUNTY',
                                    'Per capitaincome': 'PER_CAPITA', 
                                    'Medianhouseholdincome': 'MEDIAN_HOUSEHOLD',  
                                    'Medianfamilyincome': 'MEDIAN_FAMILY',
                                    'State, federal district or territory': 'STATE',
                                    'Population': 'POPULATION',
                                    'Number ofhouseholds': 'HOUSEHOLDS',
                                    'Rank': 'PER_CAPITA_RANK'}).astype({'POPULATION': int, 'HOUSEHOLDS': int})

    return html_crud

def get_county_health_data():
    cols = {
        'Rank':     'HEALTH_OUTCOMES_RANK',
        'Quartile': 'HEALTH_OUTCOMES_QUARTILE',
        'Rank.1':   'HEALTH_FACTORS_RANK',
        'Quartile.1':'HEALTH_FACTORS_QUARTILE'
    }

    ts = {
        'HEALTH_OUTCOMES_RANK': float,
        'HEALTH_OUTCOMES_QUARTILE': float,
        'HEALTH_FACTORS_RANK': float,
        'HEALTH_FACTORS_QUARTILE': float
    }

    xls = pd.ExcelFile("2021 County Health Rankings Data - v1.xlsx")

    ch_rankings = pd.read_excel(xls, "Outcomes & Factors Rankings", header=1)

    ch_rankings = ch_rankings[ch_rankings['Rank'] != 'NR']

    ch_rankings = ch_rankings.rename(columns=cols).astype(ts).dropna().set_index("FIPS")

    ch_rankings['HEALTH_OUTCOMES_PERCENTILE'] = (ch_rankings['# of Ranked Counties'] - ch_rankings['HEALTH_OUTCOMES_RANK']) / ch_rankings['# of Ranked Counties']

    ch_rankings['HEALTH_FACTORS_PERCENTILE'] = (ch_rankings['# of Ranked Counties'] - ch_rankings['HEALTH_FACTORS_RANK']) / ch_rankings['# of Ranked Counties']


    ## get data from subheadings
    headings = ['Length of Life', 'Quality of Life', 'Health Behaviors', 
                'Clinical Care', 'Social And Economic Factors', 'Physical Environment']

    change_dict = {}

    col_types  = {'# of Ranked Counties': float}

    for (count, h) in enumerate(headings):
        if count == 0:
            rank_name = "Rank"
        else:
            rank_name = f"Rank.{count}"

        h_underscored = "_".join(h.split(" "))

        col_name_on = f'{h_underscored}_Percentile'
        change_dict[rank_name] =  col_name_on
        col_types[col_name_on] = float


    subrankings = pd.read_excel(xls, "Outcomes & Factors SubRankings", header=1) \
                    .rename(columns=change_dict)


    subrankings = subrankings[subrankings['Length_of_Life_Percentile'] != 'NR'] \
                    .astype(col_types) \
                    .dropna()

    ## TODO: need to fix numeric types here

    cols = list(change_dict.values())

    for factor in cols:
        subrankings[factor] = (subrankings['# of Ranked Counties'] - subrankings[factor]) / subrankings['# of Ranked Counties']


    cols_to_get = list(change_dict.values())
    cols_to_get.append("FIPS")

    # only take columns we need
    subrankings = subrankings.loc[:, cols_to_get].set_index("FIPS")

    return ch_rankings.join(subrankings)

def get_size_data():
    gaz = pd.read_csv("2021_Gaz_counties_national.txt", delimiter="\t") \
            .rename(columns={'GEOID': 'FIPS'}) \
            .set_index("FIPS")

    return gaz[["ALAND_SQMI"]]


def get_ethnicity_data():
    populations = pd.read_csv("stco-mr2010-1.csv")

    whites = populations.loc[populations.IMPRACE == 1, ["STNAME", "CTYNAME", "RESPOP"]]

    whites["COUNTY"] = whites["CTYNAME"].str.replace("County", "")

    grouped = whites.groupby(["STNAME", "COUNTY"]).sum("RESPOP") \
                    .reset_index() \
                    .rename(columns={"RESPOP": "CAUCASIAN_POP", "STNAME": "STATE"})

    return grouped



def get_all_data():
    vd = get_vax_data()
    fatality_data = get_covid_fatality_data(vd)
    income_data = get_county_income_data()
    health_data = get_county_health_data()
    size_data = get_size_data()
    #eth_data = get_ethnicity_data()

    #.merge(eth_data, on=['STATE', 'COUNTY']) \
        
    all_data = fatality_data.reset_index() \
        .merge(income_data, on=['STATE', 'COUNTY']) \
        .set_index("FIPS") \
        .join(health_data) \
        .join(size_data)

    all_data['DENSITY'] = all_data['POPN'] / all_data['ALAND_SQMI']

    ## TODO: need to drop stuff where we have zeroes (eg Utah reporting 0 fatalities at county level)

    return all_data