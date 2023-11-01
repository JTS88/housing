import json
import pathlib
import pickle

import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel

DEMOGRAPHICS_PATH = 'data/zipcode_demographics.csv'  # path to CSV with demographics
MODEL_DIR = 'model'  # Directory where model will be loaded
MODEL_FILE = 'model.pkl'
FEATURES_FILE = 'model_features.json'

app = FastAPI()


class PriceRequest(BaseModel):
    bedrooms: int
    bathrooms: float
    sqft_living: int
    sqft_lot: int
    floors: float
    waterfront: int
    view: int
    condition: int
    grade: int
    sqft_above: int
    sqft_basement: int
    yr_built: int
    yr_renovated: int
    zipcode: str
    lat: float
    long: float
    sqft_living15: int
    sqft_lot15: int


def make_prediction(df: pd.DataFrame) -> {}:
    # add in the demographics data for this zipcode and remove any columns not in feature list
    fq_data = df.merge(demographics, how='left', on='zipcode')[features]

    # do the prediction
    prediction = model.predict(fq_data)

    return {'estimated_price': prediction[0]}


@app.post('/api/price2')
async def estimate_price2(request: Request):
    json_req = await request.json()
    req_features = {k: v for (k, v) in json_req.items() if k in features2}
    query_data = pd.DataFrame([req_features])

    return make_prediction(query_data)


@app.post('/api/price')
async def estimate_price(request_data: PriceRequest):
    # convert the data from PriceRequest into a dataframe
    query_data = pd.DataFrame([request_data.dict()])

    return make_prediction(query_data)


def load_demographics(demographics_path: str) -> pd.DataFrame:
    dgdata = pd.read_csv(demographics_path, dtype={'zipcode': str})

    return dgdata


def load_model(model_path: str, model_file: str, feature_list: str):
    model_dir = pathlib.Path(model_path)

    model = pickle.load(open(model_dir / model_file, 'rb'))
    features = json.load(open(model_dir / feature_list, 'r'))

    return model, features


# load up the models from disk
demographics = load_demographics(DEMOGRAPHICS_PATH)
model, features = load_model(MODEL_DIR, MODEL_FILE, FEATURES_FILE)

# the second API needs the zipcode added so it will extract it from the request body
features2 = features + ['zipcode']

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('serve_model:app', host='0.0.0.0', port=8000, workers=1)
