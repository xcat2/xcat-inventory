#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
# common helper subroutines
#
import os
import re
import subprocess
import json
import yaml
import globalvars

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

def loadfile(filename):
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
