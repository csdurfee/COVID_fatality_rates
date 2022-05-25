import pandas as pd

def get_covid_fatality_data(cache=True):
    if cache:
        from pathlib import Path
        COVID_DEATHS_URL  = str(Path(__file__).parent) + "/cache/time_series_covid19_deaths_US.csv"
    else:
        COVID_DEATHS_URL  = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

    deaths_df = pd.read_csv(COVID_DEATHS_URL)


    ## FIXME: get the last column of the time series rather than '2/28/22' 
    # hardcoded.
    translate_cols = { 
        # 3/11/20 was the day COVID offically named pandemic by WHO
        '3/11/21': 'DEATHS_FIRST_YEAR',
        '3/11/22': 'DEATHS',
        
        # these are based on when they became > 50% of cases in the US 
        # (eyeballing https://www.nytimes.com/interactive/2021/health/coronavirus-variant-tracker.html)
        '3/10/21': 'ALPHA_START',
        '6/10/21': 'DELTA_START',
        '12/15/21': 'OMICRON_START',

        'Admin2': 'COUNTY',
        'Province_State': 'STATE' 
    }

    cols = list(translate_cols.keys())
    cols.append("FIPS")

    deaths_cleaned = deaths_df.loc[:, cols].rename(columns=translate_cols)

    covid_df = deaths_cleaned.set_index("FIPS")

    #.dropna() ### something's happening here!!! what it is ain't exactly clear!
    ## majority of counties in Nebraska are getting torched.
    ## this is because they don't report booster coverage, I think

    covid_df['DEATHS_SECOND_YEAR'] = covid_df["DEATHS"] - covid_df["DEATHS_FIRST_YEAR"]
    covid_df['ALPHA_DEATHS'] = covid_df['DELTA_START'] - covid_df['ALPHA_START']
    covid_df['DELTA_DEATHS'] = covid_df['OMICRON_START'] - covid_df['DELTA_START']
    covid_df['OMICRON_DEATHS'] = covid_df['DEATHS'] - covid_df['OMICRON_START']


    ## there are 3 small counties in Nebraska that report negative death rates in year 2
    # FIPS -- 31023, 31033, 31123
    ## I haven't investigated why
    return covid_df.loc[covid_df.DEATHS_SECOND_YEAR > 0] \
        .drop(columns=["ALPHA_START", "DELTA_START", "OMICRON_START"])


def get_covid_daily_fatalities():
    del_cols = ["UID", "iso2", "iso3", "code3", "Admin2", "Province_State",
                "Country_Region", "Lat", "Long_", "Combined_Key", "Population"]
    
    deaths_df = pd.read_csv(COVID_DEATHS_URL, parse_dates = True)

    melted = deaths_df.drop(columns=del_cols).melt(id_vars=["FIPS"], var_name="Date", value_name="Deaths")

    # convert dates from string
    melted['Date'] = melted["Date"].astype("datetime64[ns]")

    return melted


def get_death_counts(monthly=True):
    ## for every month from April 2020 to March 2022:
    ##   get the death total at that point in time
    ##   calculate the diffs to get the monthly death totals.
    if monthly:
        snapshot_dates = pd.date_range(start="3/1/2020", end="3/1/2022", freq="M")
    else:
        snapshot_dates = pd.date_range(start="3/1/2020", end="3/1/2022", freq="Q")

    daily_df = get_covid_daily_fatalities().set_index("Date")

    pit_counts = []
    diffs = {}

    for date in snapshot_dates:
        as_str = date.strftime("%Y-%m-%d")
        point_in_time_count = daily_df.loc[as_str, ["FIPS", "Deaths"]].set_index("FIPS")

        if len(pit_counts) > 0:
            # this is ugly =(
            period_change = point_in_time_count - pit_counts[-1]
            diffs[as_str] = period_change

        # set up diffs for next iteration
        pit_counts.append(point_in_time_count)
        prev_date = date

    return diffs

def get_death_corrs(monthly=True):
    ### for each monthly death count, get the correlations of other factors so they can
    ### be plotted as a series.
    corrs = {}

    all_data = get_all_data()
    mdc = get_death_counts(monthly)
    for (month, counts) in mdc.items():
        month_joined = all_data.join(counts.rename(columns={'Deaths': "THIS_MONTH_DEATHS"}))
        month_joined['MONTHLY_PER_CAPITA_DEATH_RATE'] = month_joined['THIS_MONTH_DEATHS'] / month_joined['POPN']
        corrs[month] = month_joined.corr()['MONTHLY_PER_CAPITA_DEATH_RATE']
    return corrs