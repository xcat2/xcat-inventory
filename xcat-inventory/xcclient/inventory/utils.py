#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
# common helper subroutines
#
from __future__ import print_function
import os
import re
import subprocess
import json
import yaml
import sys
import globalvars
from exceptions import *

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

#remove the dict entries whose value is null or ''
def Util_rmnullindict(mydict):
    for key in mydict.keys():
        if isinstance(mydict[key],dict):
            Util_rmnullindict(mydict[key])
            if not mydict[key].keys():
                del mydict[key]
        else:
            if not mydict[key]:
                del mydict[key]


# replace the "{{x}}" variables in the value of dict "mydict" 
# with the values of "vardict[x]"
def Util_subvarsindict(mydict,vardict):
    for key in mydict.keys():
        if isinstance(mydict[key],dict):
            Util_subvarsindict(mydict[key],vardict)
        elif isinstance(mydict[key],list):
            for idx,val in enumerate(mydict[key]):
                if isinstance(val,str):
                    mydict[key][idx]=re.sub(r'\{\{(.*)\}\}',lambda m:vardict.get(m.group(1)),val)
        elif isinstance(mydict[key],str):
            mydict[key]=re.sub(r'\{\{(.*)\}\}',lambda m:vardict.get(m.group(1)),mydict[key])
            

# get the dict value mydict[a][b][c] with key path a.b.c
def Util_getdictval(mydict,keystr):
    if not  isinstance(mydict,dict):
        return None
    dictkeyregex=re.compile("([^\.]+)\.?(\S+)*")
    result=re.findall(dictkeyregex,keystr)
    if result:
        (key,remdkey)=result[0]
        if key not in mydict.keys():
            return None
        if remdkey:
            return Util_getdictval(mydict[key],remdkey)
        else:
            return mydict[key]

# get the dict value mydict[a][b][c] with key path a.b.c
def Util_setdictval(mydict,keystr,value):
    dictkeyregex=re.compile("([^\.]+)\.?(\S+)*")
    result=re.findall(dictkeyregex,keystr)
    if result:
        (key,remdkey)=result[0]
        if remdkey:
            if key not in mydict.keys():
                mydict[key]={}
            Util_setdictval(mydict[key],remdkey,value)
        else:
            mydict[key]=value

#remove dict key [a][b][c] with key path a.b.c
def Util_deldictkey(mydict,keystr):
    dictkeyregex=re.compile("([^\.]+)\.?(\S+)*")
    result=re.findall(dictkeyregex,keystr)
    if result:
        (key,remdkey)=result[0]
        if remdkey:
            if key not in mydict.keys():
                mydict[key]={}
            Util_deldictkey(mydict[key],remdkey)
        else:
            del mydict[key]


def loadfile(filename):
    if not os.path.exists(filename):
        raise FileNotExistException("Error: File '%s' does not exist, please check..." % filename)

    contents={}
    fmt = 'json'
    with open(filename,"r") as fh:
        f=fh.read()
        if not f.startswith('{'):
            fmt = 'yaml'
        try:
            contents=json.loads(f)
        except ValueError:
            try:
                contents = yaml.load(f)
            except Exception,e:
                raise InvalidFileException("Error: failed to load file \"%s\", please validate the file with 'yamllint %s'(for yaml format) or 'cat %s|python -mjson.tool'(for json format)!"%(filename,filename,filename))
        return contents, fmt
    return None, fmt

#initialize the global vars in globalvars.py
def initglobal():
    if os.path.exists("/var/run/xcatd.pid"):
        globalvars.isxcatrunning=1
    else:
        globalvars.isxcatrunning=0 
    if globalvars.isxcatrunning:
        (retcode,out,err)=runCommand("XCATBYPASS=0 lsxcatd -v")
    else:
        (retcode,out,err)=runCommand("XCATBYPASS=1 lsxcatd -v")
    if retcode!=0:
        xcat_version=""
    globalvars.xcat_version=out.strip()
    globalvars.xcat_verno=globalvars.xcat_version.split(' ')[1]

# if "key" of d1 or "key" of d1[key] not in d2, delete it
def filter_dict_keys(d1, d2):
    tmp_d1 = d1
    for key in tmp_d1.keys():
        if key not in d2:
            del tmp_d1[key]
            continue
        if type(tmp_d1[key]) != dict:
            continue
        for subkey in tmp_d1[key].keys():
            if subkey not in d2[key]:
                del tmp_d1[key][subkey]
    return tmp_d1

#print if -v|--verbose specified
def verbose(message,file=sys.stdout):
    if globalvars.verbose:
        print("%s"%(message),file=file)

#get home directory of the current user
def gethome():
    home = os.path.expanduser("~")
    return home



