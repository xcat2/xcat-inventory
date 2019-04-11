FROM centos:7

MAINTAINER The xCAT Project

ENV container docker

RUN yum install -y -q gcc python-devel python-virtualenv postgresql-devel && \
    yum clean all

WORKDIR /xcat-apiserver
COPY xcat-inventory/main.py .
COPY xcat-inventory/xcclient ./xcclient
COPY xcat-inventory/requirements.txt .

RUN virtualenv /venv && \
    source /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

