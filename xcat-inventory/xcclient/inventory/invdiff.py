#!/usr/bin/python
from __future__ import print_function
import deepdiff
import pprint
import yaml
import json
import sys


def loadfile(filename):
    contents={}
    with open(filename,"r") as fh:
        f=fh.read()
        try:
            contents=json.loads(f)
        except ValueError:
            try:
                contents = yaml.load(f)
            except Exception,e:
                raise InvalidFileException("Error: failed to load file \"%s\", please validate the file with 'yamllint %s'(for yaml format) or 'cat %s|python -mjson.tool'(for json format)!"%(location,location,location))
        return contents
    return None

def dump2yaml(xcatobj, location=None):
    if not location:
        print(yaml.safe_dump(xcatobj, default_flow_style=False,allow_unicode=True))
    else:
        f=open(location,'w')
        print(yaml.safe_dump(xcatobj, default_flow_style=False,allow_unicode=True),file=f)

    #TODO: store in file or directory

def dump2json(xcatobj, location=None):
    if not location:
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        f=open(location,'w')
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')),file=f)


def json2dict(jsonstr):
    return json.loads(jsonstr)

if(len(sys.argv)!=3):
    print("invdiff <file1> <file2>",file=sys.stderr)
    exit(1)

fn1=sys.argv[1]
fn2=sys.argv[2]


d1=loadfile(filename=fn1)
d2=loadfile(filename=fn2)




dt=deepdiff.DeepDiff(d1,d2,ignore_order=True,report_repetition=False,exclude_paths='',significant_digits=None,view='text',verbose_level=2)
print(dump2yaml(dict(dt)))
