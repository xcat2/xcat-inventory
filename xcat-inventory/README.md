# xcat-inventory - A tool to manipulate inventory data in xCAT cluster

xcat-inventory is an inventory tool for the cluster managed by xCAT(http://xcat.org), the feature includes:

- a object based view of the cluster inventory, which is flexible, extensible and well formatted

- interfaces to export/import the cluster inventory data in yaml/json format, which can be then managed under source control

- inventory templates for typical clusters, which help user to defines a cluster easily

- ability to intergrate with Ansible(Comming Soon)

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

Download "xcat-inventory" from #url# to xCAT management node, and run `yum install xcat-inventory.rpm` to install it

## dependency

Several python packages are required:

* Psycopg: PostgreSQL adapter for the Python
* SQLAlchemy(above 0.8.0): Python SQL toolkit and Object Relational Mapper
* PyMySQL(0.7.x): a pure-Python MySQL client library
* PyYAML: YAML parser and emitter for the Python
* Six: a Python 2 and 3 compatibility library

In most cases, these packages will be installed during `xcat-inventory` installation. 
If you are prompted that some of them cannot be found during `xcat-inventory` installation, you can download the package from #dep-url# and install it manually 
If you are prompted `No module named xxx` when you run `xcat-inventory`, you can install the missing package with one of the following way: 

* install the corresponding rpm/deb package
* install the python package with `pip`
* download the python package tarball from PyPi(https://pypi.python.org/pypi), uncompress it and install the package with `python setup.py install`

## platform

The `xcat-inventory` is arch independent, i.e, you can install it on `X86_64`,`ppc64`, or `ppc64le` xCAT management nodes 

Currently, rpm package is shipped, it can be installed on Linux distribution like Redhat 7.x, CentOS 7.x and SuSE. The installation and function verification is finished on rhels7.x. For other Linux distributions, you might need to handle the dependency issue by yourself. 

`xcat-inventory` is compatible with xCAT with same release

## command synopsis

### help

Show usage info

```
[root@c910f03c05k21 xcat-inventory]# xcat-inventory help
usage: xcat-inventory [--debug] [-v] [-V] <subcommand> ...

xCAT inventory management tool

Positional arguments:
  <subcommand>
    export       Export the inventory data from xcat database
    help         Display help about this program or one of its subcommands.
    import       Import inventory file to xcat database

Optional arguments:
  --debug        Prints debugging output into the log file (not implemented
                 yet).
  -v, --verbose  Prints verbose output (not implemented yet).
  -V, --version  Shows the program version and exits.

See "xcat-inventory help COMMAND" for help on a specific command.
```

### export

Export the inventory data from xcat database 

```
[root@c910f03c05k21 xcat-inventory]# xcat-inventory help export
usage: xcat-inventory export [-t <type>] [-o <name>] [-f <path>]
                             [-s <version>] [--format <format>]

Export the inventory data from xcat database

Arguments:
  -t <type>, --type <type>
                        type of objects to export, valid values:
                        node,network,passwd,route,site,osimage,policy. If not
                        specified, all objects in xcat databse will be
                        exported
  -o <name>, --objects <name>
                        names of the objects to export, delimited with
                        Comma(,). If not specified, all objects of the
                        specified type will be exported
  -f <path>, --path <path>
                        path of the inventory file(not implemented yet)
  -s <version>, --schema-version <version>
                        schema version of the inventory data. Valid values:
                        2.0,3.0,latest,1.0. If not specified, the "latest"
                        schema version will be used
  --format <format>     format of the inventory data, valid values: json,
                        yaml. json will be used by default if not specified
 ```
 
 ### import

Import inventory file to xcat database
 
 ```                    
[root@c910f03c05k21 xcat-inventory]# xcat-inventory help import
usage: xcat-inventory import [-t <type>] [-o <name>] [-f <path>]
                             [-s <version>] [--dry] [-c]

Import inventory file to xcat database

Arguments:
  -t <type>, --type <type>
                        type of the objects to import, valid values:
                        node,network,passwd,route,site,osimage,policy. If not
                        specified, all objects in the inventory file will be
                        imported
  -o <name>, --objects <name>
                        names of the objects to import, delimited with
                        Comma(,). If not specified, all objects of the
                        specified type in the inventory file will be imported
  -f <path>, --path <path>
                        path of the inventory file to import
  -s <version>, --schema-version <version>
                        schema version of the inventory file. Valid schema
                        versions: 2.0,3.0,latest,1.0. If not specified, the
                        "latest" schema version will be used
  --dry                 Dry run mode, nothing will be commited to xcat
                        database
  -c, --clean           clean mode. IF specified, all objects other than the
                        ones to import will be removed
[root@c910f03c05k21 xcat-inventory]#
```




## reporting bugs

For any bugs or feature request, please open ticket in #github issues#



