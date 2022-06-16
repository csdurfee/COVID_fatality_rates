import pandas as pd

def add_suffix(df, suff='CHR'):
    add_suff = {}
    for col in df.columns:
        new_col_name = f"{col} ({suff})"
        add_suff[col] = new_col_name
    return df.rename(columns=add_suff)

def get_ranked_data(config):
    if config.USE_CACHE:
        COUNTY_HEALTH_URL = config.CACHE_DIR + \
            "/2019 County Health Rankings Data - v3.xls"
    else:
        COUNTY_HEALTH_URL = "https://www.countyhealthrankings.org/sites/default/files/media/document/2019%20County%20Health%20Rankings%20Data%20-%20v3.xls"

    xls = pd.ExcelFile(COUNTY_HEALTH_URL)
    foo = pd.read_excel(xls, "Ranked Measure Data", header=1)

    cols = [
        'Years of Potential Life Lost Rate',
        '% Fair/Poor',
        'Physically Unhealthy Days',
        'Mentally Unhealthy Days',
        '% Smokers',
        '% Obese',
        '% Physically Inactive',
        '% Excessive Drinking',
        '% Alcohol-Impaired',
        'Chlamydia Rate',
        'Teen Birth Rate',
        '% Uninsured',
        'PCP Rate',
        'Dentist Rate',
        'MHP Rate',
        'Preventable Hosp. Rate',
        '% Screened',
        '% Vaccinated',
        '% Some College',
        '% Unemployed',
        '% Children in Poverty',
        'Income Ratio',
        '% Single-Parent Households',
        'Violent Crime Rate',
        'Injury Death Rate',
        '% Severe Housing Problems'
    ]
    return add_suffix(foo.set_index("FIPS").loc[:, cols])

def get_additional_measure_data(config):
    if config.USE_CACHE:
        COUNTY_HEALTH_URL = config.CACHE_DIR + \
            "/2019 County Health Rankings Data - v3.xls"
    else:
        COUNTY_HEALTH_URL = "https://www.countyhealthrankings.org/sites/default/files/media/document/2019%20County%20Health%20Rankings%20Data%20-%20v3.xls"

    xls = pd.ExcelFile(COUNTY_HEALTH_URL)
    measure_data = pd.read_excel(xls, "Additional Measure Data", header=1)

    cols = ['Life Expectancy', 
            'Age-Adjusted Mortality',
            'Infant Mortality Rate', 
            'Child Mortality Rate',
            'Drug Overdose Mortality Rate', 
            '% Insufficient Sleep',
            'Homicide Rate', 
            'Firearm Fatalities Rate', 
            '% Non-Hispanic White',
            '% Frequent Physical Distress',
            '% Frequent Mental Distress',
            'Age-Adjusted Mortality (Black)', 
            'Age-Adjusted Mortality (Hispanic)',
            '% Rural',
            '% Homeowners',
            '% African American',
            '% Asian',
            '% Hispanic',
            '% Female',
            'Segregation index', 
            '% Food Insecure',
            '% Diabetic',
            'HIV Prevalence Rate',
            'MV Mortality Rate',
            '% Disconnected Youth',
            '% Free or Reduced Lunch'
            ]

    return add_suffix(measure_data.set_index("FIPS").loc[:, cols])

def get_county_health_data(config):
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

    if config.USE_CACHE:
        COUNTY_HEALTH_URL = config.CACHE_DIR + \
            "/2019 County Health Rankings Data - v3.xls"
    else:
        COUNTY_HEALTH_URL = "https://www.countyhealthrankings.org/sites/default/files/media/document/2019%20County%20Health%20Rankings%20Data%20-%20v3.xls"

    xls = pd.ExcelFile(COUNTY_HEALTH_URL)

    ch_rankings = pd.read_excel(xls, "Outcomes & Factors Rankings", header=1)

    ch_rankings = ch_rankings[ch_rankings['Rank'] != 'NR']

    ch_rankings = ch_rankings.rename(columns=cols).astype(ts).dropna().set_index("FIPS")

    ch_rankings['HEALTH_OUTCOMES_PERCENTILE'] = (ch_rankings['# of Ranked Counties'] - ch_rankings['HEALTH_OUTCOMES_RANK']) / ch_rankings['# of Ranked Counties']

    ch_rankings['HEALTH_FACTORS_PERCENTILE'] = (ch_rankings['# of Ranked Counties'] - ch_rankings['HEALTH_FACTORS_RANK']) / ch_rankings['# of Ranked Counties']


    ## get data from subheadings
    headings = ['Length of Life', 'Quality of Life', 'Health Behaviors', 
                'Clinical Care', 'Social & Economic Factors', 'Physical Environment']

    change_dict = {}

    col_types  = {'# of Ranked Counties': float}

    for (count, h) in enumerate(headings):
        if count == 0:
            rank_name = "Rank"
        else:
            rank_name = f"Rank.{count}"

        col_name_on = f'{h} Percentile'
        change_dict[rank_name] =  col_name_on
        col_types[col_name_on] = float

    subrankings = pd.read_excel(xls, "Outcomes & Factors SubRankings", header=1) \
                    .rename(columns=change_dict)

    subrankings = subrankings[subrankings['Length of Life Percentile'] != 'NR'] \
                    .astype(col_types) \
                    .dropna()

    cols = list(change_dict.values())

    for factor in cols:
        subrankings[factor] = (subrankings['# of Ranked Counties'] - subrankings[factor]) / subrankings['# of Ranked Counties']

    cols_to_get = list(change_dict.values())
    cols_to_get.append("FIPS")

    # only take columns we need
    subrankings = subrankings.loc[:, cols_to_get].set_index("FIPS")

    ret = ch_rankings.join(subrankings)
    return add_suffix(ret)

def get_opioid_data():
    """US County Opioid Dispensing rates"""
    #url = "https://www.cdc.gov/drugoverdose/rxrate-maps/county2019.html"
    url = "county2019.html"

    data = pd.read_html(url)
    return data[0].drop(["State", "County"], axis=1).set_index("County FIPS Code")

def get_social_vuln_data(config):
    """
    The CDC's 2018 Social Vulnerability Index
    """
    # doc: https://www.atsdr.cdc.gov/placeandhealth/svi/documentation/pdf/SVI2018Documentation-H.pdf
    if config.USE_CACHE:
        SOCIAL_VULN_URL   = config.CACHE_DIR + "/SVI2018_US_COUNTY.csv"
    else:
        SOCIAL_VULN_URL   = "https://svi.cdc.gov/Documents/Data/2018_SVI_Data/CSV/SVI2018_US_COUNTY.csv" 
 
    df = pd.read_csv(SOCIAL_VULN_URL)
    ## these are the estimated percents (EP_)
    cols = [x for x in df.columns if x.startswith("EP_")]

    rename_cols = {
        'EP_POV':  '% Below Poverty Line (SVI)',
        'EP_UNEMP': '% Unemployed (SVI)',
        'EP_PCI':   'Per Capita Income (SVI)',
        'EP_NOHSDP': '% No HS Diploma (SVI)',
        'EP_AGE65': '% Over 65 (SVI)',
        'EP_AGE17': '% Under 17 (SVI)',
        'EP_DISABL': '% Disabled (SVI)',
        'EP_SNGPNT': '% Single Parent Households (SVI)',
        'EP_MINRTY': '% Minority (SVI)',
        'EP_LIMENG': '% Limited English (SVI)',
        'EP_MUNIT':  '% Multiunit Housing (SVI)',
        'EP_MOBILE': '% Mobile Homes (SVI)',
        'EP_CROWD': '% Crowded Living (SVI)',
        'EP_NOVEH': '% No Vehicle (SVI)',
        'EP_GROUPQ': '% In Group Quarters (SVI)',
        'EP_UNINSUR': '% Uninsured (SVI)'
    }

    return df.loc[df.EP_POV > -999, :].set_index("FIPS").loc[:, cols].rename(columns=rename_cols)

