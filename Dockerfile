FROM centos:7

MAINTAINER The xCAT Project

ENV container docker

RUN yum install -y -q python-devel python-virtualenv ansible && \
    yum clean all

WORKDIR /opt/xcat-inventory
COPY xcat-inventory/main.py .
COPY xcat-inventory/xcclient ./xcclient
COPY xcat-inventory/requirements.txt .

RUN virtualenv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PYTHONPATH /opt/xcat-inventory/venv/lib/python2.7/site-packages
