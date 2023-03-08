### BUILD THE IMAGE
# Use ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:22.04

# Install python 3.10 & pip
RUN apt update
RUN apt install build-essential -y
RUN apt install libsqlite3-dev -y
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update 
RUN apt install python3.10 -y
RUN apt install python3-pip -y

# Specify our path in the container
WORKDIR /api_spec

RUN pip3 install requests
RUN pip3 install pytest

# CMD python3 minitwit_simulator.py "http://server:5000/sim"


