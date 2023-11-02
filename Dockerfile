#
# build the image with: docker build -t phdata:0 .
# run the image with: docker run -p 8000:8000 phdata:0
#

FROM continuumio/anaconda3:2023.09-0

WORKDIR /project

COPY . .

RUN conda env create -f conda_environment.yml

CMD [ "conda", "run", "-n", "housing", "--no-capture-output", "uvicorn", "serve_model:app", "--host", "0.0.0.0", "--port", "8000", \
     "--reload", "--reload-include", "model/model*" ]
