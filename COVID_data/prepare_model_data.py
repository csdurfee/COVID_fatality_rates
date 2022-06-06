from multiprocessing.reduction import DupFd
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

IMPUTATION_THRESHOLD = .1
TEST_SIZE = 0.2
MIN_POP = 50000 # limit to counties with over this population

def normalize(X):
    scaler = StandardScaler().fit(X)
    return scaler.transform(X)

def get_cols_to_drop_and_impute(df):
    cols_to_drop   = []
    cols_to_impute = []
    missing_counts = {}
    max_missing = IMPUTATION_THRESHOLD * len(df)

    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_counts[col] = missing_count
        if missing_count > max_missing:
            cols_to_drop.append(col)
        elif missing_count > 0:
            cols_to_impute.append(col)

    return (cols_to_drop, cols_to_impute, missing_counts)

def impute(df, to_impute):
    """
    impute with median value
    """
    for col in to_impute:
        df[col] = df[col].fillna(df[col].median())
    return df

def get_non_numeric(df):
    non_numeric = []
    for col in df.columns:
        if df[col].dtype == 'object':
            non_numeric.append(col)
    return non_numeric
    
def make_train_test(df, year=1, min_pop=MIN_POP):
    """
    Take raw dataframe and convert it to imputed/scaled numeric values,
    and split into train & test for building model
    """
    # drop counties below population threshold
    if min_pop:
        df = df[df.POPULATION > min_pop]

    # drop text (non-numeric fields)
    df = df.drop(get_non_numeric(df), axis=1)

    # drop/impute cols with missing data
    to_drop, to_impute, missing_counts = get_cols_to_drop_and_impute(df)
    df = df.drop(to_drop, axis=1)
    df = impute(df, to_impute)

    ## generate y: whether in top quantile of death rates or not.
    if year == 1:
        quantiles = pd.qcut(df.DEATH_RATE_FIRST_YEAR, 4, labels=False)
    else:
        quantiles = pd.qcut(df.DEATH_RATE_SECOND_YEAR, 4, labels=False)

    y = (quantiles == 3)

    # drop fields that are 'cheating' (raw death counts and death rates)
    death_cols = [x for x in df.columns if x.find("DEATH") > -1]
    print(f"dropping {death_cols}")
    df = df.drop(death_cols, axis=1)

    (x_train, x_test, y_train, y_test) = train_test_split(df, y, test_size = TEST_SIZE)
    x_train = normalize(x_train)
    x_test = normalize(x_test)
    return (x_train, x_test, y_train, y_test, df)