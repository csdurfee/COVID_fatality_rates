import pandas as pd

def get_vax_data(config):
    if config.USE_CACHE:
        VAX_URL = config.CACHE_DIR + "/vaccinetracking/vacc_data/data_county_current.csv"
    else:
        VAX_URL = "https://github.com/bansallab/vaccinetracking/blob/main/vacc_data/data_county_current.csv"

    vax_df = pd.read_csv(VAX_URL, parse_dates=['DATE'])

    ## take only county-level data.
    ## rename to make usage of column clear
    vax_df = vax_df[vax_df.GEOFLAG == 'County'].rename(columns={'COUNTY': 'FIPS'})

    vax_df = vax_df.drop(['STATE', 'WEEK', 'YEAR'], axis=1)



    partial  = vax_df[vax_df.CASE_TYPE == 'Partial Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    booster  = vax_df[vax_df.CASE_TYPE == 'Booster Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")
    complete = vax_df[vax_df.CASE_TYPE == 'Complete Coverage'].pivot_table("CASES", "FIPS", "CASE_TYPE")

    return partial.join(booster).join(complete).rename(
        columns={   'Partial Coverage': 'COVID Partial Coverage',
                    'Booster Coverage': 'COVID Booster Coverage',
                    'Complete Coverage':'COVID Complete Coverage'}
    )
