import json

import pandas as pd
import requests

DATA_PATH = 'data/future_unseen_examples.csv'

PRICE_URL = 'http://localhost:8000/api/price'


def load_test_data(data_path: str) -> pd.DataFrame:
    test_data = pd.read_csv(data_path,
                            dtype={'zipcode': str})

    return test_data


def main():
    test_data = load_test_data(DATA_PATH)

    test_dict = test_data.to_dict(orient='records')

    for rec in test_dict:
        response = requests.post(PRICE_URL, json=rec)
        jb = json.loads(response.content)
        print('Estimated price: ${0:.2f}'.format(jb['estimated_price']))
        #break


if __name__ == "__main__":
    main()
