from sklearn.linear_model import (
    RidgeClassifier,
    LogisticRegression,
    SGDClassifier
)
from sklearn.ensemble import (
    AdaBoostClassifier,
    RandomForestClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier
)
from sklearn.svm import SVC, NuSVC, LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, RadiusNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.gaussian_process import GaussianProcessClassifier

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

def get_model(config):
    """
    gets model from librares
    args:
        config: dict-like configuration
    return:
        classifier model
    """
    classifier_class = eval(config["classifier_class"])

    classifier = classifier_class(**config["classifier_params"])
    return classifier

if __name__=="__main__":
    sklearn_config = dict(
        classifier_class = "RandomForestClassifier",
        classifier_params = dict(
            n_estimators = 50,
            max_depth = 10
        )
    )
    print(get_model(sklearn_config))
    xgboost_config = dict(
        classifier_class = "XGBClassifier",
        classifier_params = dict(
            tree_method="hist",
            early_stopping_rounds=3
        )
    )
    print(get_model(xgboost_config))
    lightgbm_config = dict(
        classifier_class = "LGBMClassifier",
        classifier_params = dict(
            boosting_type="gbdt",
            max_depth=3
        )
    )
    print(get_model(lightgbm_config))
    catboost_config = dict(
        classifier_class = "CatBoostClassifier",
        classifier_params = dict(
            iterations=500,
            depth=8
        )
    )
    print(get_model(catboost_config))