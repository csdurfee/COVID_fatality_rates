import pandas as pd

def get_vax_data(cached=True):
    if cached:
        VAX_URL = "vaccinetracking/vacc_data/data_county_current.csv"
    else:
        VAX_URL = "https://github.com/bansallab/vaccinetracking/blob/main/vacc_data/data_county_current.csv"

    vax_df = pd.read_csv(VAX_URL, parse_dates=['DATE'])

    ## take only county-level data.
    ## rename to make usage of column clear
    vax_df = vax_df[vax_df.GEOFLAG == 'County'].rename(columns={'COUNTY': 'FIPS'})

    ## drop stuff that doesn't matter and rename coverage columns to be statsmodels.formula friendly
    vax_df = vax_df.drop(['STATE', 'WEEK', 'YEAR'], axis=1) \
                .rename(columns={'Partial Coverage': 'Partial_Coverage',
                                 'Booster Coverage': 'Booster_Coverage',
                                 'Complete Coverage': 'Complete_Coverage'})


    partial  = vax_df[vax_df.CASE_TYPE == 'Partial Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    booster  = vax_df[vax_df.CASE_TYPE == 'Booster Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    complete = vax_df[vax_df.CASE_TYPE == 'Complete Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")

    popn_by_fips = vax_df.loc[vax_df.CASE_TYPE == 'Partial Coverage', ['POPN', 'FIPS']
                                ].set_index('FIPS')

    return partial.join(booster).join(complete).join(popn_by_fips)

def get_size_data():
    gaz = pd.read_csv("2021_Gaz_counties_national.txt", delimiter="\t") \
            .rename(columns={'GEOID': 'FIPS'}) \
            .set_index("FIPS")

    return gaz[["ALAND_SQMI"]]

def get_political_data(cache=False):
    if cache:
        POLITICAL_DATA    = "countypres_2000-2016.csv"
    else:
        POLITICAL_DATA    = None # FIXME
    voting_df = pd.read_csv(POLITICAL_DATA)

    voting_df = voting_df.loc[(voting_df.year == 2016) & (voting_df.party == "republican"), 
                            ["FIPS", "candidatevotes", "totalvotes"]] \
                    .dropna() \
                    .set_index("FIPS") \
                    .rename(columns={"candidatevotes": "2016_repub_votes", 
                                    "totalvotes": "2016_total_votes"}) \
                    .dropna() ## there are only 3 counties (all in Alaska) with no data here.
    
    voting_df['REPUB_PARTISAN'] = voting_df['2016_repub_votes'] / voting_df['2016_total_votes']
    voting_df["REPUB_QUARTILE"] = pd.qcut(voting_df['REPUB_PARTISAN'], 4, labels=False)

    return voting_df
