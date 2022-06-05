import pandas as pd
import requests
import zipfile
import io

def get_size_data(config):
    if config.USE_CACHE:
        url = config.CACHE_DIR + "/2021_Gaz_counties_national.txt"
        df = pd.read_csv(url, delimiter="\t")
    else:
        zip_url = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2021_Gazetteer/2021_Gaz_counties_national.zip"
        zipped = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(zipped.content))
        raw_data = z.open("2021_Gaz_counties_national.txt")
        df = pd.read_csv(raw_data, delimiter="\t")


    gaz = df.rename(columns={'GEOID': 'FIPS'}) \
            .set_index("FIPS")

    return gaz[["ALAND_SQMI"]]
