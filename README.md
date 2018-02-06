# xcat-inventory

A tool to backup/restore the xcat cluster configuration
=============================================

Usage Info:

A. the syntax of command to export the xcat inventory data(for specific type, specific objects, or the whole cluster):  
```
xcat-inventory export [--format=<yaml/json>] [-t|--type=<node/osimage/site/policy/passwd/network/router>] [-o|--objects=<object list delimited with ','>]

```
  1. to generate the inventory data for all osimage in yaml format
  ```
  xcat-inventory export --format=yaml -t osimage 
  ```
  
  2. to generate the inventory data for some nodes
  ```
  xcat-inventory export --format=yaml -t node -o c910f03c05k27,virtswitch1
  ```
  
  3. to generate the inventory data for the who cluster
  ```
  xcat-inventory export --format=yaml
  ```
  the inventory data can be redirected to inventory file with `>`



B. the syntax to import the inventory data to xcat is:
```
xcat-inventory import -f|--path <the path to inventory file> [-t|--type=<node/osimage/site/policy/passwd/network/router>] [-o|--objects=<object list delimited with ','>]
```
  1. to import  the definition of node virtswitch1  from the full inventory file
  ```
  xcat-inventory import -f /tmp/cluster -t node -o virtswitch1
  ```
  2. to import all the definitions of osimages from the full inventory file
  ```
  xcat-inventory import -f /tmp/cluster -t osimage
  ```
  3. to import the inventory file of the whole cluster
  ```
  xcat-inventory import -f /tmp/cluster
  ```

==========================================================

Typical User Cases:

A. xCAT cluster configuration under source control
----------------------------------------------------------
In the production xCAT cluster, there are lots of changes on the cluster configuration everyday, for example, replacing failed nodes, modifying global configuration in site table, the customzation of osimages, etc. Cluster administrators are always requested to rollback the cluster to some desired snapshot and collaborate with each other between the work shifts, things will become much  easy if the cluster confguration can be under source control. "xcat-inventory" is a useful tool for xCAT to interact with version control system such as GIT, SVN, etc. 

A typical user case to manage xCAT cluster configuration data  is described below: 

1. create a directory "cluster-data" under git
```
mkdir -p /git/cluster-data
cd /git/cluster-data
git init
```

2. export the current cluster configuration to a YAML file "clusterinv.yaml" under "/git/cluster-data"
```
xcat-inventory export --format=yaml >/git/cluster-data/clusterinv.yaml
```

3. check the diff of the cluster configuration and commit the cluster data(commit no: c95673b861ded3c962a7659522a01fc96af6b89b) 
```
git diff 
git add /git/cluster-data/clusterinv.yaml
git commit /git/cluster-data/clusterinv.yaml -m "$(date "+%Y_%m_%d_%H_%M_%S"): replaced bad nodes; turn on xcatdebugmode;blabla"
```

4. ordinary cluster operation

5. find the desired cluster configuration commit(commit no: c95673b861ded3c962a7659522a01fc96af6b89b), check it out and apply it
```
git checkout  c95673b861ded3c962a7659522a01fc96af6b89b
xcat-inventory import -f /git/cluster-data/clusterinv.yaml
``` 



 
