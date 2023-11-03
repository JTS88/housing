# Sound Realty Home Price Estimator 

The prototype model provided estimates home prices based on prior sales and
demographic data.  The as-delivered model used the following fields to estimate prices:
- price
- bedrooms
- bathrooms
- sqft_living
- sqft_lot
- floors
- sqft_above
- sqft_basement
- all the fields in the zipcode_demographics file

The model that is built is a K-nearest neighbor regression model which will
find the five most similar properties and take the average of those prices as the estimate for a future property.

The model was trained using 75% of the records in kc_house_data.csv for training and the
remaining 25% for testing.  The R-squared score for this model using just the features
above was 0.728143 where a perfect score would be 1.0.  This means that 73% of the estimated price can be explained
by the feature data in kc_house_data and zipcode_demographics, the remaining 27% is due to other factors.

The best score of 0.795002 was achieved by adding in the following features from kc_house_data.csv:
- zipcode
- waterfront
- view
- condition
- grade

Additional features from the data file did not improve the result so they were left out.

Two additional model types were tested using the same features listed above.
The first model was a Random Forest Regression model which builds multiple decision
trees from the training data.  The results from all the decision trees are then averaged
to determine a price.  The best score achieved with Random Forest regression was 0.861959.

The final model type was Gradient Boosting Regression.  This model also builds a series of
decision trees but instead of collecting the results from all trees and returning the mean,
it chains the trees together to fine-tune the prediction.  The best result from the Gradient
Boosting Regressor was 0.855570.

Based on the results from testing the three model types, the Random Forest Regressor would be the
suggested model using the following fields from the data file:

- price
- bedrooms
- bathrooms
- sqft_living
- sqft_lot
- floors
- sqft_above
- sqft_basement
- zipcode
- waterfront
- view
- condition
- grade
- demographic data that matches the property's zip code

### Technical Discussion
The code had two minor issues which I fixed.  The first was that the load_data() function was not using the
parameter ```demographics_path``` as the line that created the dataframe was hard-coded to load the demographics data:

```demographics = pandas.read_csv("data/zipcode_demographics.csv",```

The other issue was the constant that was supposed to point to the demographics file location was incorrect:

```DEMOGRAPHICS_PATH = "data/kc_house_data.csv"  # path to CSV with demographics```

was corrected to:

```DEMOGRAPHICS_PATH = "data/zipcode_demographics.csv"  # path to CSV with demographics```

#### Scoring method
I used the R<sup>2</sup> score to evaluate the features and regressor types simply because it is easier to grasp.
For the KNN model I left the default n_neighbors at 5.  I added the features and recorded the scores:

| R<sup>2</sup> score | configuration |
|---------------------|-------------- |
| 0.545778            | no demo, no zip, stock feature list |
| 0.728143            | with demo, no zip, stock feature list |
| 0.732538            | with demo, with zip, stock feature list |
| 0.734610            | with demo, with zip, with waterfront |
| 0.768964            | with demo, with zip, with waterfront, with view |
| 0.768137            | with demo, with zip, with waterfront, with view, with condition |
| * 0.795002          | with demo, with zip, with waterfront, with view, with condition, with grade |
| 0.794592            | with demo, with zip, with waterfront, with view, no condition, with grade |
| 0.793324            | with demo, with zip, with waterfront, with view, with condition, with grade, with yr_built |
| 0.778465            | with demo, with zip, with waterfront, with view, with condition, with grade, with yr_built, with yr_renovated |

I also used Boruta to suggest which features were not needed.  Here are the results:

```
BorutaPy finished running.

Iteration: 	10 / 10
Confirmed: 	11
Tentative: 	2
Rejected: 	24

------Support and Ranking for each feature------
Doesn't pass the test:  bedrooms  - Ranking:  14
Passes the test:  bathrooms  - Ranking:  1
Passes the test:  sqft_living  - Ranking:  1
Passes the test:  sqft_lot  - Ranking:  1
Doesn't pass the test:  floors  - Ranking:  18
Passes the test:  waterfront  - Ranking:  1
Passes the test:  view  - Ranking:  1
Doesn't pass the test:  condition  - Ranking:  20
Passes the test:  grade  - Ranking:  1
Passes the test:  sqft_above  - Ranking:  1
Doesn't pass the test:  sqft_basement  - Ranking:  3
Doesn't pass the test:  zipcode  - Ranking:  4
Doesn't pass the test:  ppltn_qty  - Ranking:  6
Doesn't pass the test:  urbn_ppltn_qty  - Ranking:  15
Doesn't pass the test:  sbrbn_ppltn_qty  - Ranking:  26
Doesn't pass the test:  farm_ppltn_qty  - Ranking:  24
Doesn't pass the test:  non_farm_qty  - Ranking:  12
Doesn't pass the test:  medn_hshld_incm_amt  - Ranking:  11
Passes the test:  medn_incm_per_prsn_amt  - Ranking:  1
Passes the test:  hous_val_amt  - Ranking:  1
Doesn't pass the test:  edctn_less_than_9_qty  - Ranking:  17
Doesn't pass the test:  edctn_9_12_qty  - Ranking:  2
Doesn't pass the test:  edctn_high_schl_qty  - Ranking:  8
Doesn't pass the test:  edctn_some_clg_qty  - Ranking:  12
Doesn't pass the test:  edctn_assoc_dgre_qty  - Ranking:  9
Doesn't pass the test:  edctn_bchlr_dgre_qty  - Ranking:  5
Doesn't pass the test:  edctn_prfsnl_qty  - Ranking:  2
Doesn't pass the test:  per_urbn  - Ranking:  10
Doesn't pass the test:  per_sbrbn  - Ranking:  26
Doesn't pass the test:  per_farm  - Ranking:  26
Doesn't pass the test:  per_non_farm  - Ranking:  22
Doesn't pass the test:  per_less_than_9  - Ranking:  23
Doesn't pass the test:  per_9_to_12  - Ranking:  19
Doesn't pass the test:  per_hsd  - Ranking:  7
Doesn't pass the test:  per_some_clg  - Ranking:  20
Doesn't pass the test:  per_assoc  - Ranking:  16
Passes the test:  per_bchlr  - Ranking:  1
Passes the test:  per_prfsnl  - Ranking:  1
```


#### Random forest regressor
I ran a few different configurations of the RF regressor and recorded the following results.

| R<sup>2</sup> score | configuration                                         |
| -------- |-------------------------------------------------------|
| 0.857996 | num estimators 500                                    |
| 0.861959 | num estimators 100                                    |
| 0.848293 | num estimators 100 - only columns suggested by Boruta |

So far the best result has been with RF using 100 estimators.

#### Gradient boosting regressor
I only ran a single configuration of the Gradient Boosting Regressor

| R<sup>2</sup> score | configuration  |
|----------|---------------------------|
| 0.855570 | num estimators 100 |


To further assess how the different model types handle the data, I ran a 10-fold
cross-validation on each model type and ran three samples from each model type.
The mean accuracy and standard deviation are listed below:

| Model | mean accuracy | std dev |
| ----- |---------------| ------- |
| KNN | 0.818323      | 0.025136 |
| | 0.818323      | 0.025136 |
| | 0.818323      | 0.025136 |
| Random forest | 0.872931  | 0.014670 |
| | 0.872928      | 0.016054 |
| | 0.872830      | 0.015690 |
| Grad boosting | 0.869445      | 0.014515 |
| | 0.869241      | 0.014402 |
| | 0.869517      | 0.014451 |

The Random Forest Regressor produced the highest mean accuracy while the Gradient Boosting
had a slightly lower standard deviation.

#### Scaling
The project uses FastAPI in Docker container.  One thought for scaling would be to increase
the number of workers that uvicorn starts.  Unfortunately this cannot be changed without
restarting the service.  Another issue with the number of workers is the other requirement
that the model can be updated without restarting the service.  As mentioned below, the file
watcher that will detect a new model and restart the service cannot be used with more than
one worker.

Given that a Docker container can run only one instance of the service, I would suggest using
Kubernetes or Docker Swarm or other coordination service based on the cloud provider.

For production deployments a more robust front-end would be appropriate.  Nginx is a popular
proxy server that is lightweight and can balance the load and prevent the FastAPI service from
attacks.

#### Updating without downtime
The approach I chose was to use the file watcher feature in uvicorn.  I configured it to
watch for file modifications in the model/ directory.  If either model.pkl or model_features.json
is updated, uvicorn will detect it and restart the service.
If there is only one service running, there will be some downtime while the service restarts
but if there are multiple containers running, no downtime should be experienced.

To complete the solution, the model files would need to be mounted outside the Docker
container and all containers would ideally use the same shared directory.  Using the same
mount point for all containers would mean that updating the model only requires copying the
new model files to one location instead of having to find all Docker hosts and updating
them individually.