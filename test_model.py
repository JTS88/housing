import json

import pandas as pd
import requests

DATA_PATH = 'data/future_unseen_examples.csv'

PRICE_URL = 'http://localhost:8000/api/price2'


def load_test_data(data_path: str) -> pd.DataFrame:
    test_data = pd.read_csv(data_path, dtype={'zipcode': str}).drop(columns=['sqft_living15', 'sqft_lot15'])

    return test_data


def main():
    test_data = load_test_data(DATA_PATH)

    test_dict = test_data.to_dict(orient='records')

    # for i in range(25):
    #     print('Starting loop')
    for rec in test_dict:
        response = requests.post(PRICE_URL, json=rec)
        if response.status_code == 200:
            jb = json.loads(response.content)
            print('Estimated price: ${0:.2f}'.format(jb['estimated_price']))
        else:
            print(f'Got an error {response.status_code} from the server.\n    Message is: {response.text}')


if __name__ == "__main__":
    main()
