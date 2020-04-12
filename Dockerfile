FROM python:3.8-slim

WORKDIR /microservice

COPY ./requirements.txt /microservice/requirements.txt

RUN apt-get update && apt-get install gcc -y && apt-get clean

RUN pip install -r /microservice/requirements.txt && rm -rf /root/.cache/pip

COPY . /microservice/
