FROM python:2.7
RUN apt-get update && apt-get install -y python-dev python3-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev build-essential
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements/common.txt /code/
RUN pip install -r common.txt
ADD . /code/
