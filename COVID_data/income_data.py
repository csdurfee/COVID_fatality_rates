import pandas as pd

def get_county_income_data(config):
    if config.USE_CACHE:
        PER_CAPITA_URL    =  config.CACHE_DIR + "/percapita.html"
    else:
        PER_CAPITA_URL    = "https://en.wikipedia.org/wiki/List_of_United_States_counties_by_per_capita_income"
    
    conversions = {
        'Population': int,
        'Number ofhouseholds': int
    }

    html_crud = pd.read_html(PER_CAPITA_URL)[2]

    # this will make rows with "-" in them (which are summary rows) be nan
    html_crud['Rank'] = pd.to_numeric(html_crud['Rank'], errors="coerce")

    html_crud = html_crud.dropna()

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
        'Rank': 'PER_CAPITA_RANK'}) \
        .astype({'POPULATION': int, 
                 'HOUSEHOLDS': int})
    return html_crud