### BUILD THE IMAGE
# Use ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:22.04

RUN apt update
RUN apt install build-essential -y
RUN apt install libsqlite3-dev -y

# Install python 3.10 & pip
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update 
RUN apt install python3.10 -y
RUN apt install python3-pip -y

# Specify our path in the container
WORKDIR /minitwit

# We copy everything from this path
COPY ./requirements.txt /minitwit

# Install requirements from requirements.txt
RUN pip3 install -r /minitwit/requirements.txt

COPY . /minitwit

RUN gcc flag_tool.c -lsqlite3

RUN ./control.sh init 
RUN python3 manage.py migrate

# ### What to do when running the container
CMD python3 ./manage.py runserver 0.0.0.0:8000 --noreload