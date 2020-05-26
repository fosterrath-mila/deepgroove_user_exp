FROM ubuntu:18.04

RUN apt-get update

RUN apt-get install -y python3-pip libsndfile1-dev

COPY . /var/local/src/deepgroove_user_exp

RUN pip3 install /var/local/src/deepgroove_user_exp

RUN pip3 install gunicorn

EXPOSE 8000
