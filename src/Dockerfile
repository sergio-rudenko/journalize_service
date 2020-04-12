# pull official base image
FROM python:3.8-slim


# set work directory
WORKDIR /usr/src/project


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# copy requirements file
COPY ./requirements.txt /usr/src/project/requirements.txt


# install dependencies
RUN apt-get update \
    && apt-get install postgresql-client -y \
    && apt-get clean

RUN pip install -r /usr/src/project/requirements.txt \
    && rm -rf /root/.cache/pip


# copy startup script
COPY ./wait-for-postgres.sh /usr/src/project/wait-for-postgres.sh
RUN chmod a+x /usr/src/project/wait-for-postgres.sh


# copy application
COPY ./app /usr/src/project/app/
