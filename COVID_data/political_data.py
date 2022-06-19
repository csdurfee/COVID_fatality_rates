import pandas as pd

def get_political_data(config):
    if config.USE_CACHE:
        POLITICAL_DATA    = config.CACHE_DIR + "/countypres_2000-2016.csv"
    else:
        POLITICAL_DATA    = "https://raw.githubusercontent.com/MEDSL/county-returns/master/countypres_2000-2016.csv"
    voting_df = pd.read_csv(POLITICAL_DATA)

    voting_df = voting_df.loc[(voting_df.year == 2016) & (voting_df.party == "republican"), 
                            ["FIPS", "candidatevotes", "totalvotes"]] \
                    .dropna() \
                    .set_index("FIPS") \
                    .rename(columns={"candidatevotes": "2016_repub_votes", 
                                     "totalvotes": "2016_total_votes"}) \
                    .dropna() ## there are only 3 counties (all in Alaska) with no data here.
    
    voting_df['2016 Repub Vote Share'] = voting_df['2016_repub_votes'] / voting_df['2016_total_votes']

    return voting_df