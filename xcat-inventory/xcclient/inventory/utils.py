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

