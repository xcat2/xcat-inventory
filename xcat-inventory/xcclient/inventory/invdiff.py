#!/usr/bin/python
from __future__ import print_function
import deepdiff
import pprint
import yaml
import json
import sys
import subprocess
import re


class InvalidFileException(Exception):
    pass

def runCommand(cmd, env=None):
    """
    Run one command only, when you don't want to bother setting up
    the Popen stuff.
        (retcode,out,err)=runCommand('lsxcatd -v')
    """
    try:
        p = subprocess.Popen(cmd,
        env=env,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        out, err = p.communicate()
    except OSError,e:
        return p.returncode,out, err
    return p.returncode,out, err


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
                raise InvalidFileException("Error: failed to load file \"%s\", please validate the file with 'yamllint %s'(for yaml format) or 'cat %s|python -mjson.tool'(for json format)!"%(filename,filename,filename))
        return contents
    return None

def dump2yaml(xcatobj, filename=None):
    if not filename:
        print(yaml.safe_dump(xcatobj, default_flow_style=False,allow_unicode=True))
    else:
        f=open(filename,'w')
        print(yaml.safe_dump(xcatobj, default_flow_style=False,allow_unicode=True),file=f)

    #TODO: store in file or directory

def dump2json(xcatobj, filename=None):
    if not filename:
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        f=open(filename,'w')
        print(json.dumps(xcatobj, sort_keys=True, indent=4, separators=(',', ': ')),file=f)


def json2dict(jsonstr):
    return json.loads(jsonstr)

if(len(sys.argv)!=4):
    print("invdiff <file1> <file2>",file=sys.stderr)
    exit(1)

print("\n====================BEGIN=====================\n")
fn1=sys.argv[1]
fn2=sys.argv[2]
fn3=sys.argv[3]

#print("file1=%s"%(fn1))
#print("file2=%s"%(fn2))

if fn1=="/dev/null":
    print("--- %s"%(fn1),file=sys.stdout)
    print("+++ %s\n"%(fn3),file=sys.stdout)
    exit(0)

if fn2=="/dev/null":
    print("--- %s"%(fn3),file=sys.stdout)
    print("+++ %s\n"%(fn2),file=sys.stdout)
    exit(0)


try:
    d1=loadfile(filename=fn1)
    d2=loadfile(filename=fn2)
except InvalidFileException,e:
    (retcode,out,err)=runCommand("diff -u %s %s"%(fn1,fn2))    
    if out:
        out=re.sub(r"%s"%(fn2),fn3,out)
        print(out,file=sys.stdout) 
    if err:
        err=re.sub(r"%s"%(fn2),fn3,err)
        print(err,file=sys.stderr) 
    print("\n===================END======================\n")
    exit(retcode)


dt=deepdiff.DeepDiff(d1,d2,ignore_order=True,report_repetition=False,exclude_paths='',significant_digits=None,view='text',verbose_level=2)

print("\n--- %s\n+++ %s"%(fn3,fn3))
pprint.pprint(dt,indent=2)
#exit(0)
#print(dump2yaml(json.loads(dt.json)))
#print(dump2yaml((dt.json)))
print("\n====================END=====================\n")
