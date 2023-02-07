### BUILD THE IMAGE
# Install ubuntu image https://hub.docker.com/_/ubuntu
FROM ubuntu:22.04

RUN apt update
RUN apt install build-essential -y
RUN apt install libsqlite3-dev -y

# Install python
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update 
RUN apt install python3.10 -y
RUN apt install python3-pip -y

# Specify our path in the container
WORKDIR /minitwit

# We copy everything from this path
COPY . /minitwit

RUN pip3 install -r /minitwit/requirements.txt

RUN gcc flag_tool.c -lsqlite3
RUN ./control.sh init

# We assign the specific port for the localhost
EXPOSE 5000

# ### What to do when running the container
CMD python3 ./minitwit.py