from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

IMPUTATION_THRESHOLD = .1
TEST_SIZE = 0.2

"""
    y = bank_data['y'].copy()
    x = bank_data.copy().drop(['y'], axis=1)

    
"""

def tt_split(X, y):
    return train_test_split(X, y, test_size = TEST_SIZE)

def normalize(train_x, train_y, test_x, test_y):
    pass

def get_cols_to_drop_and_impute(df):
    """
    We will impute any metric that has less than THRESHOLD% 
    """
    cols_to_drop   = []
    cols_to_impute = []
    max_missing = IMPUTATION_THRESHOLD * len(df)

    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > max_missing:
            cols_to_drop.append(col)
        elif missing_count > 0:
            cols_to_impute.append(col)

    return (cols_to_drop, cols_to_impute)

def impute(df, to_impute):
    """
    impute with mean value
    """
    for col in to_impute:
        col_mean = df[col].mean()
        df[col].fillna(col_mean)

    return df

def get_non_numeric(df):
    non_numeric = []
    for col in df.columns:
        if df[col].dtype == 'object':
            non_numeric.append(col)
    return non_numeric
    
def make_train_test(df):
    non_numeric = get_non_numeric(df)

    # drop text (non-numeric fields)
    numeric_only = df.drop(non_numeric, axis=1)

    # figure out what cols are too sparse to impute or not
    to_drop, to_impute = get_cols_to_drop_and_impute(numeric_only)

    dropped = numeric_only.drop(to_drop, axis=1)

    imputed = impute(dropped, to_impute)

    # TODO: make 'X' and 'y'

    (train_x, train_y, test_x, test_y) = normalize(tt_split(imputed))
    return (train_x, train_y, test_x, test_y)