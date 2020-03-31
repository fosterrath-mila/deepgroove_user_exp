FROM ubuntu:18.04

RUN apt-get update

RUN apt-get install -y python3-pip

COPY . /var/local/src/deepgroove_user_exp

RUN pip3 install /var/local/src/deepgroove_user_exp

RUN pip3 install gunicorn

EXPOSE 5000

ENTRYPOINT ["gunicorn", "deepgroove_web_user_experiment:APP"]

CMD ["-w", "4", "-preload", "-b", "0.0.0.0:5000"]
