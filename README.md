# xcat-inventory - A Infrastructure-as-Code(IaC) cluster management system based on xCAT

[**xcat-inventory**](https://github.com/xcat2/xcat-inventory/wiki/xcat-inventory--Wiki) is an inventory tool for the cluster managed by [**xCAT**](http://xcat.org), the features include:

- a object based view of the cluster inventory, which is flexible, extensible and well formatted

- interfaces to export/import the cluster inventory data in yaml/json format

- inventory templates for typical clusters, which help user to define a cluster easily

- native ability to manage cluster configuration under source control(see [Cookbook](https://github.com/xcat2/xcat-inventory/wiki/How-to-source-control-xCAT-Cluster-configuration-with-%22xcat-inventory%22%3F))

- automatic cluster deployment according to the cluster definition(Comming soon)

- ability to intergrate with Ansible(Comming soon)

The typical workflow:

![alt text](https://github.com/xcat2/xcat-inventory/blob/master/workflow.jpg)


## Table of Contents

- [Installing](#installing)
- [Building](#building)
- [Dependencies](#dependency)
- [Development](#development)
- [Platform Restrictions](#platform)
- [Cookbooks](#Cookbooks)
- [Typical use cases](#usecase)
  - [Version control of cluster inventory data](#versioncontrol)
  - [define and create a xCAT cluster inventory](#definecluster)
- [Reporting bugs](#reporting-bugs)


## Installing

Download "xcat-inventory" package from [xcat-inventory](https://github.com/xcat2/xcat-inventory/releases/download/v0.1.4/xcat-inventory-0.1.4-c4.noarch.rpm) to xCAT management node, and run `yum install xcat-inventory.rpm` to install it.

## Building

```
# git clone https://github.com/xcat2/xcat-inventory.git
Cloning into 'xcat-inventory'...
remote: Counting objects: 1844, done.
remote: Compressing objects: 100% (7/7), done.
remote: Total 1844 (delta 0), reused 6 (delta 0), pack-reused 1837
Receiving objects: 100% (1844/1844), 401.48 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1072/1072), done.
```

```
# cd xcat-inventory
# git checkout master
Already on 'master'
# git pull upstream master --tags
From github.com:xcat2/xcat-inventory
 * branch            master     -> FETCH_HEAD
Already up-to-date.
# ./makepythonrpm xcat-inventory
...
Building /root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4*.noarch.rpm ...
/root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4-c10.noarch.rpm
```
## Development

### Python virtualenv

```
# yum install -y yum install -y -q gcc python-devel python-virtualenv postgresql-devel
# git clone https://github.com/xcat2/xcat-inventory.git [ -b <tag|branch> ]
# cd xcat-inventory/xcat-inventory
# virtualenv venv
# source venv/bin/activate
# pip install --upgrade pip
# pip install -r requirements.txt
# FLASK_DEBUG=1 python main.py
```

### Docker container
```
# git clone https://github.com/xcat2/xcat-inventory.git [ -b <tag|branch> ]
# cd xcat-inventory
# docker build -f ./Dockerfile -t xcat-apiserver .
# docker tag xcat-apiserver xcatdevops/xcat-apiserver:latest
```

You can tag and push it to your dock registry (for example, xcatdevops/xcat-apiserver:latest), and then you can run it on an xCAT management node with below:

```
docker run -it -v /etc/xcat:/etc/xcat -v `pwd`/xcat-inventory:/xcat-apiserver -p 5000:5000 xcatdevops/xcat-apiserver /bin/bash
# source /venv/bin/activate
# FLASK_DEBUG=1 python main.py

```
## Dependency

Several python packages are required:

* Psycopg: PostgreSQL adapter for the Python
* SQLAlchemy(above 0.8.0): Python SQL toolkit and Object Relational Mapper
* PyMySQL(0.7.x): a pure-Python MySQL client library
* PyYAML: YAML parser and emitter for the Python
* Six: a Python 2 and 3 compatibility library
* deepdiff: Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes
* configparser: a module working with configuration files
* sh: a full-fledged subprocess replacement for Python 2.6 - 3.6, PyPy and PyPy3 that allows you to call any program as if it were a function

In most cases, these packages will be installed during `xcat-inventory` installation. 

If you are prompted that some of them cannot be found during `xcat-inventory` installation, you can download the package from [dep-url](http://xcat.org/files/xcat/xcat-dep/2.x_Linux/beta/xcat-inventory/) and install it manually. 

If you are prompted `No module named xxx` when you run `xcat-inventory`, you can install the missing package with one of the following way: 

* install the corresponding rpm/deb package
* install the python package with `pip`
* download the python package tarball from PyPi(https://pypi.python.org/pypi), uncompress it and install the package with `python setup.py install`

## Platform Restrictions

The `xcat-inventory` is arch independent, i.e, you can install it on xCAT management nodes with architecture `X86_64`,`ppc64`, or `ppc64le` 

Currently, only rpm package is shipped, which can be installed on Linux distributions like Redhat 7.x, CentOS 7.x and SuSE. 

The installation and function verification is finished on rhels7.x. 

For other Linux distributions, you might need to handle the dependency issue by yourself. 


## Cookbooks

See [Cookbooks](https://github.com/xcat2/xcat-inventory/wiki)


## Blueprints

See [Designs](https://github.com/xcat2/xcat-inventory/wiki#mini-designs-of-xcat-inventory-major-features)

## Usecase

This section presents some typical usecases [xcat-inventory usecase](http://xcat-docs.readthedocs.io/en/latest/advanced/xcat-inventory/index.html)

## Reporting bugs

For any bugs or feature request, please open ticket in [issues](https://github.com/xcat2/xcat-inventory/issues)



