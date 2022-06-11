"""
NEXT THINGS NEXT:
    * Limit model to counties over 50,000 people so we can get more stats
    * see what dropping is still happening after that.

"""


import pandas as pd
from COVID_data.prepare_model_data import *
from COVID_data import all_data

class config:
    USE_CACHE = True
    CACHE_DIR = "/Users/caseydurfee/msds/data_mining_final_project/cache"

df = all_data.get_all_data(config)

(x_train, x_test, y_train, y_test, cols) = make_train_test(df)


from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
clf = RandomForestClassifier()
clf.fit(x_train, y_train)
# score = clf.score(x_test, y_test)

# print(score)


from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
pred = clf.predict(x_test)

fpr, tpr, _ = roc_curve(y_test, pred)
roc_auc = roc_auc_score(y_test, pred)

print(roc_auc)


