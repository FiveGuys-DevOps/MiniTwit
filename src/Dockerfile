### BUILD THE IMAGE
# Use ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:22.10

RUN apt update
RUN apt install build-essential -y
RUN apt install libsqlite3-dev -y

# Install python 3.10 & pip
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update 
RUN apt install python3.10 -y
RUN apt install python3-pip -y
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

# Specify our path in the container
WORKDIR /minitwit

# We copy everything from this path
COPY ./requirements.txt /minitwit

# Install requirements from requirements.txt
RUN pip3 install -r /minitwit/requirements.txt
 
ENV TZ=Europe/Berlin
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install python3-venv python3-dev postgresql postgresql-contrib curl -y

COPY . /minitwit

# RUN apt install postgresql postgresql-contrib -y
RUN pip3 install psycopg2
