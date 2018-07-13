# xcat-inventory - A tool to manipulate inventory data in xCAT cluster

xcat-inventory is an inventory tool for the cluster managed by xCAT(http://xcat.org), the features include:

- a object based view of the cluster inventory, which is flexible, extensible and well formatted

- interfaces to export/import the cluster inventory data in yaml/json format, which can be then managed under source control

- inventory templates for typical clusters, which help user to define a cluster easily

- ability to intergrate with Ansible(Comming soon)

## Table of Contents

- [Installing](#installing)
- [Dependencies](#dependency)
- [Platform Restrictions](#platform)
- [Command Synopsis](#command-synopsis)
  - [help](#help)
  - [export](#export)
  - [import](#import)
- [Typical use cases](#usecase)
  - [Version control of cluster inventory data](#versioncontrol)
  - [define and create a xCAT cluster inventory](#definecluster)
- [Reporting bugs](#reporting-bugs)


## installing

Download "xcat-inventory" package from [xcat-inventory](https://github.com/xcat2/xcat-inventory/releases/download/v0.1.4/xcat-inventory-0.1.4-c4.noarch.rpm) to xCAT management node, and run `yum install xcat-inventory.rpm` to install it

## dependency

Several python packages are required:

* Psycopg: PostgreSQL adapter for the Python
* SQLAlchemy(above 0.8.0): Python SQL toolkit and Object Relational Mapper
* PyMySQL(0.7.x): a pure-Python MySQL client library
* PyYAML: YAML parser and emitter for the Python
* Six: a Python 2 and 3 compatibility library

In most cases, these packages will be installed during `xcat-inventory` installation. 

If you are prompted that some of them cannot be found during `xcat-inventory` installation, you can download the package from [dep-url](http://xcat.org/files/xcat/xcat-dep/2.x_Linux/beta/xcat-inventory/) and install it manually. 

If you are prompted `No module named xxx` when you run `xcat-inventory`, you can install the missing package with one of the following way: 

* install the corresponding rpm/deb package
* install the python package with `pip`
* download the python package tarball from PyPi(https://pypi.python.org/pypi), uncompress it and install the package with `python setup.py install`

## platform

The `xcat-inventory` is arch independent, i.e, you can install it on xCAT management nodes with architecture `X86_64`,`ppc64`, or `ppc64le` 

Currently, only rpm package is shipped, which can be installed on Linux distributions like Redhat 7.x, CentOS 7.x and SuSE. 

The installation and function verification is finished on rhels7.x. 

For other Linux distributions, you might need to handle the dependency issue by yourself. 


## command synopsis

### help

Show usage info:

```
# xcat-inventory help
# xcat-inventory export -h
# xcat-inventory import -h
```

### export

Export the inventory data from xcat database: 

* dump cluster inventory data to screen
```
# xcat-inventory export
```
* dump cluster inventory data to screen in yaml format
```
# xcat-inventory export --format yaml
```
* dumo cluster inventory data to screen in json format
```
# xcat-inventory export --format json
```
* dump cluster inventory data to a file 
```
# xcat-inventory export -f /tmp/cluster
```
* dump osimage inventory data to a file
```
# xcat-inventory export -t osimage -f /tmp/osimage
``` 
* dump the inventory data of osimage "rhels6.5-x86_64-netboot-compute" to a file
```
# xcat-inventory export -t osimage -o rhels6.5-x86_64-netboot-compute  -f /tmp/osimage
```
* export cluster inventory data to a directory
```
# xcat-inventory export -d /tmp/mm/
The osimage objects has been exported to directory /tmp/mm/osimage
The cluster inventory data has been dumped to /tmp/mm/cluster.json
```
   all objects except "osimage" are dumped to a file "cluster.json" or "cluster.yaml", "osimage" objects are exported to osimage directories under a subdirectory "osimage". 

   Each osimage direcotry contains a "definition.yaml" or "definition.json", and the customized osimage files(files which are not under directory `/opt/xcat/share/xcat/`), such as `pkglist`,`otherpkglist`,`synclists`,`partitionfile`,`template` and `exlists` 
* export an osimage objec to a directory
```
# xcat-inventory export -t osimage -o rhels7.4-ppc64le-install-service  -d /tmp/mm/osimage/
```
 
 ### import

* Import cluster inventory file to xcat database
 
```                    
# xcat-inventory import -f /tmp/cluster
```
* Import "node" and "network" objects from inventory file to xcat database
```
# xcat-inventory import -f /tmp/cluster  -t node,network
```
* Import a network object from cluster inventory file
```
# xcat-inventory import -f /tmp/cluster  -t network -o 192_168_122_0-255_255_255_0
```
* Import cluster inventory data from an inventory directory
```
# xcat-inventory import -d /tmp/mm/
```
* Import an osimage object from cluster inventory directory
```
# xcat-inventory import -d /tmp/mm/ -t osimage -o sles12.2-ppc64le-install-compute
```
* Import an osimage inventory directory
```
# xcat-inventory import -d /tmp/mm/osimage/rhels7.4-x86_64-netboot-compute/
``` 
* Import osimage inventory file with variables
```
# xcat-inventory import -e GITREPO=/tmp/ -e SWDIR=/tmp -f /tmp/osimage/osimage.withvar.yaml
```

## usecase

This section presents some typical usecases [xcat-inventory usecase](http://xcat-docs.readthedocs.io/en/latest/advanced/xcat-inventory/index.html)

## reporting bugs

For any bugs or feature request, please open ticket in [issues](https://github.com/xcat2/xcat-inventory/issues)



