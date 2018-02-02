# xCAT-Incubator

the syntax of command to export the xcat inventory data(for specific type, specific objects, or the whole cluster):  
```
xcat-inventory export --format=<yaml/json> [-t|--type=<node/osimage/site/policy/passwd/network/router> -o|--objects=<object list delimited with ','>]

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

the syntax to import the inventory data to xcat is:
```
xcat-inventory import -f|--path <the path to inventory file> [-t|--type=<node/osimage/site/policy/passwd/network/router> -o|--objects=<object list delimited with ','>]
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
xcat-inventory import -f /tmp/cluster```
```
