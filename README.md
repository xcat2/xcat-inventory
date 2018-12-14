# xcat-inventory - A Infrastructure-as-Code(IaC) cluster management system based on xCAT

xcat-inventory is an inventory tool for the cluster managed by xCAT(http://xcat.org), the features include:

- a object based view of the cluster inventory, which is flexible, extensible and well formatted

- interfaces to export/import the cluster inventory data in yaml/json format

- inventory templates for typical clusters, which help user to define a cluster easily

- native ability to manage cluster configuration under source control(Comming soon)

- automatic cluster deployment according to the cluster definition(Comming soon)

- ability to intergrate with Ansible(Comming soon)

## Table of Contents

- [Installing](#installing)
- [Building](#building)
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


## Installing

Download "xcat-inventory" package from [xcat-inventory](https://github.com/xcat2/xcat-inventory/releases/download/v0.1.4/xcat-inventory-0.1.4-c4.noarch.rpm) to xCAT management node, and run `yum install xcat-inventory.rpm` to install it

## Building

```
[root@boston01 ~]# git clone https://github.com/xcat2/xcat-inventory.git
Cloning into 'xcat-inventory'...
remote: Counting objects: 1844, done.
remote: Compressing objects: 100% (7/7), done.
remote: Total 1844 (delta 0), reused 6 (delta 0), pack-reused 1837
Receiving objects: 100% (1844/1844), 401.48 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1072/1072), done.
[root@boston01 ~]#
```

```
[root@boston01 ~]# cd xcat-inventory
[root@boston01 ~]# git checkout master
Already on 'master'
[root@boston01 ~]# git pull upstream master --tags
From github.com:xcat2/xcat-inventory
 * branch            master     -> FETCH_HEAD
Already up-to-date.
[root@boston01 xcat-inventory]# ./makepythonrpm xcat-inventory
xcat-inventory/
xcat-inventory/cli/
xcat-inventory/cli/xcat-inventory
:
:
:
xcat-inventory/requirements.txt
Building /root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4*.noarch.rpm ...
/root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4-c10.noarch.rpm
[root@boston01 xcat-inventory]#
```

```
[root@boston01 xcat-inventory]# yum -y install /root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4-c10.noarch.rpm
Loaded plugins: product-id, search-disabled-repos, subscription-manager
This system is not registered with an entitlement server. You can use subscription-manager to register.
Examining /root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4-c10.noarch.rpm: 1:xcat-inventory-0.1.4-c10.noarch
Marking /root/rpmbuild/RPMS/noarch/xcat-inventory-0.1.4-c10.noarch.rpm as an update to 1:xcat-inventory-0.1.4-c4.noarch
Resolving Dependencies
--> Running transaction check
---> Package xcat-inventory.noarch 1:0.1.4-c4 will be updated
---> Package xcat-inventory.noarch 1:0.1.4-c10 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

=============================================================================================================================
 Package                    Arch               Version                    Repository                                    Size
=============================================================================================================================
Updating:
 xcat-inventory             noarch             1:0.1.4-c10                /xcat-inventory-0.1.4-c10.noarch             258 k

Transaction Summary
=============================================================================================================================
Upgrade  1 Package

Total size: 258 k
Downloading packages:
Running transaction check
Running transaction test
Transaction test succeeded
Running transaction
  Updating   : 1:xcat-inventory-0.1.4-c10.noarch                                                                         1/2
  Cleanup    : 1:xcat-inventory-0.1.4-c4.noarch                                                                          2/2
  Verifying  : 1:xcat-inventory-0.1.4-c10.noarch                                                                         1/2
  Verifying  : 1:xcat-inventory-0.1.4-c4.noarch                                                                          2/2

Updated:
  xcat-inventory.noarch 1:0.1.4-c10

Complete!
[root@boston01 xcat-inventory]#
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

In most cases, these packages will be installed during `xcat-inventory` installation. 

If you are prompted that some of them cannot be found during `xcat-inventory` installation, you can download the package from [dep-url](http://xcat.org/files/xcat/xcat-dep/2.x_Linux/beta/xcat-inventory/) and install it manually. 

If you are prompted `No module named xxx` when you run `xcat-inventory`, you can install the missing package with one of the following way: 

* install the corresponding rpm/deb package
* install the python package with `pip`
* download the python package tarball from PyPi(https://pypi.python.org/pypi), uncompress it and install the package with `python setup.py install`

## Platform

The `xcat-inventory` is arch independent, i.e, you can install it on xCAT management nodes with architecture `X86_64`,`ppc64`, or `ppc64le` 

Currently, only rpm package is shipped, which can be installed on Linux distributions like Redhat 7.x, CentOS 7.x and SuSE. 

The installation and function verification is finished on rhels7.x. 

For other Linux distributions, you might need to handle the dependency issue by yourself. 


## Command synopsis

### Help

Show usage info:

```
# xcat-inventory help
# xcat-inventory export -h
# xcat-inventory import -h
# xcat-inventory diff -h
```

### Export

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
 
 ### Import

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
* Import inventory file with variables, the variable values are specified in the specified variabe file. The content of variabe file is a dict in yaml format, the dict key is variable name, the dict value is the variable value.
```
# xcat-inventory import -f /tmp/osimage/osimage.withvar.yaml --env-file /tmp/env
```

The format of variables in osimage inventory file is `{{<variable name>}}`. 
* Builtin variables in inventory file
xcat-inventory exposes several builtin variables, the values of the variables are determined during `xcat-inventory import` implicitly, do not need to specify with `-e` explicitly. Please find the description and usage of the builtin variables with: 
```
# xcat-inventory envlist
```

 ### diff

* Diff the given 2 inventory files, if with `--filename` option, will show this filename 
```
# xcat-inventory diff --files /tmp/cluster.json /root/cluster.json [--filename cluster.json]
```
* Diff the given inventory file with xCAT DB, only compare the objects in given inventory file
```
# xcat-inventory diff --source /tmp/cluster.json
```
* Diff the given inventory file with whole xCAT DB
```
# xcat-inventory diff --source /tmp/cluster.json --all
```

## Usecase

This section presents some typical usecases [xcat-inventory usecase](http://xcat-docs.readthedocs.io/en/latest/advanced/xcat-inventory/index.html)

## Reporting bugs

For any bugs or feature request, please open ticket in [issues](https://github.com/xcat2/xcat-inventory/issues)



