import json
import pathlib
import pickle
from typing import List
from typing import Tuple

import numpy as np
import pandas
from boruta import BorutaPy
from sklearn import ensemble, neighbors
from sklearn import model_selection
from sklearn import pipeline
from sklearn import preprocessing
from sklearn.metrics import r2_score


SALES_PATH = "data/kc_house_data.csv"  # path to CSV with home sale data
DEMOGRAPHICS_PATH = "data/zipcode_demographics.csv"  # path to CSV with demographics
# List of columns (subset) that will be taken from home sale data
SALES_COLUMN_SELECTION = [
    'price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors',
    'sqft_above', 'sqft_basement', 'zipcode', 'waterfront', 'view', 'condition', 'grade'
]
OUTPUT_DIR = "model"  # Directory where output artifacts will be saved


def load_data(
        sales_path: str, demographics_path: str, sales_column_selection: List[str]
) -> Tuple[pandas.DataFrame, pandas.Series]:
    """Load the target and feature data by merging sales and demographics.

    Args:
        sales_path: path to CSV file with home sale data
        demographics_path: path to CSV file with home sale data
        sales_column_selection: list of columns from sales data to be used as
            features

    Returns:
        Tuple containg with two elements: a DataFrame and a Series of the same
        length.  The DataFrame contains features for machine learning, the
        series contains the target variable (home sale price).

    """
    data = pandas.read_csv(sales_path,
                           usecols=sales_column_selection,
                           dtype={'zipcode': str})
    demographics = pandas.read_csv(demographics_path,
                                   dtype={'zipcode': str})

    # dummy demographics dataframe
    # demographics = pd.DataFrame(data=[{'zipcode': '1'}])

    merged_data = data.merge(demographics, how="left",
                             on="zipcode") # .drop(columns="zipcode")

    # keep the columns suggested by boruta
    # merged_data = merged_data[[
    #     'price', 'bathrooms', 'grade', 'hous_val_amt', 'medn_incm_per_prsn_amt', 'per_bchlr', 'per_prfsnl', 'sqft_above', 'sqft_living', 'sqft_lot', 'view', 'waterfront' ]]

    # Remove the target variable from the dataframe, features will remain
    y = merged_data.pop('price')
    x = merged_data

    return x, y


def feature_selector(X, Y) -> None:
    model = ensemble.RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    feat_selector = BorutaPy(
        verbose=2,
        estimator=model,
        n_estimators='auto',
        max_iter=10  # number of iterations to perform
    )

    # train Boruta
    # N.B.: X and y must be numpy arrays
    feat_selector.fit(np.array(X), np.array(Y))

    # print support and ranking for each feature
    print("\n------Support and Ranking for each feature------")
    for i in range(len(feat_selector.support_)):
        if feat_selector.support_[i]:
            print("Passes the test: ", X.columns[i],
                  " - Ranking: ", feat_selector.ranking_[i])
        else:
            print("Doesn't pass the test: ",
                  X.columns[i], " - Ranking: ", feat_selector.ranking_[i])


def main():
    """Load data, train model, and export artifacts."""
    x, y = load_data(SALES_PATH, DEMOGRAPHICS_PATH, SALES_COLUMN_SELECTION)
    x_train, _x_test, y_train, _y_test = model_selection.train_test_split(
        x, y, random_state=42)

    # call the feature selection
    # feature_selector(x, y)

    # model = pipeline.make_pipeline(preprocessing.RobustScaler(),
    #                                neighbors.KNeighborsRegressor(n_neighbors=5)).fit(x_train, y_train)
    model = pipeline.make_pipeline(preprocessing.RobustScaler(),
                                   ensemble.RandomForestRegressor(n_estimators=100)).fit(x_train, y_train)
    # model = pipeline.make_pipeline(preprocessing.RobustScaler(),
    #                                ensemble.GradientBoostingRegressor()).fit(x_train, y_train)

    preds = model.predict(_x_test)

    r2s = r2_score(_y_test.values, preds)
    print(f'r2 score: {r2s:.6f}')

    kf = model_selection.KFold(n_splits=10, shuffle=True, random_state=43)
    scores = model_selection.cross_val_score(model, x, y, cv=kf, scoring='r2')

    print('Cross-Validation Scores:', scores)
    print(f'Mean Accuracy: {scores.mean():.6f}')
    print(f'Standard Deviation: {scores.std():.6f}')

    output_dir = pathlib.Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Output model artifacts: pickled model and JSON list of features
    pickle.dump(model, open(output_dir / "model.pkl", 'wb'))
    json.dump(list(x_train.columns),
              open(output_dir / "model_features.json", 'w'))


if __name__ == "__main__":
    main()
