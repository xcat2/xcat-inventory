#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
# helper functions for schema validation
#

from __future__ import print_function
import os
import yaml
import sys
import re

def isIPaddr(varin):
    ValidIpAddressRegex = "^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.(([0-9]|[0-9]{2}|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){2}([0-9]|[0-9]{2}|0[0-9]{2}|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
    return (re.match(ValidIpAddressRegex,str(varin)) is not None)

def isMac(varin):
    MacRegex=r'[0-9a-f]{2}([:])[0-9a-f]{2}(\1[0-9a-f]{2}){4}$'
    return (re.match(MacRegex,str(varin),re.IGNORECASE) is not None)

def isPort(varin):
    PortRegex=r'^(swp)*[0-9]+$'
    return (re.match(PortRegex,str(varin),re.IGNORECASE) is not None)

def isRegex(varin):
    RegexPattern=r'^\|.*\|$'
    return (re.match(RegexPattern,str(varin)) is not None)

def isIPrange(varin):
    ip=[]
    ip=str(varin).split('-')
    return len(ip)==2 and isIPaddr(ip[0]) and isIPaddr(ip[1])

def isMacHosts(varin):
    machosts=[]
    machosts=str(varin).split('|') 
    for machost in machosts:
        entry=[]
        entry=machost.split('!') 
        if not isMac(entry[0]):
           return False
    return True 

def isNicips(varin):
    nicips=[] 
    nicips=str(varin).split(',')
    for nicip in nicips:
        entry=[]
        entry=nicip.split('!')
        if len(entry)>2:
            return False
        ips=[]
        if len(entry) == 2:
            if isRegex(entry[1]):
                continue
            ips=entry[1].split('|')
        for ip in ips:
            if not isIPaddr(ip) or isRegex(ip):
                return False
    return True   

def underpath(filename,path):
    if re.match(r'^'+os.path.realpath(path)+r'\/',os.path.realpath(filename)):
        return True
    else:
        return False


# return a list of the files in list "infilelist" and the files included in them
def getfileanddeplist(infilelist):
    #helper function to return a dict whose keys are file "filename" specified and files included by it 
    def getincfiledict(filename,filedict={}):
        regex_include=r'^#INCLUDE:\s*([^#]+)#$'
        if filename in filedict.keys():
            return
        filedict[filename]=1
        if os.path.isfile(filename):
            with open(filename) as fileobj:
                filelines = fileobj.readlines()
            olddir=os.getcwd()
            curdir=os.path.dirname(filename)
            os.chdir(curdir)
            for line in filelines:
                matchobj_include=re.search(regex_include,line.strip()) 
                if matchobj_include:
                    incfile=matchobj_include.group(1).strip()
                    incfile=os.path.realpath(incfile)
                    if incfile not in filedict.keys():
                        getincfiledict(incfile,filedict)
            os.chdir(olddir)
        return 

    filedict={}
    for filename in infilelist:
        getincfiledict(filename,filedict)
    return filedict.keys()

def strsubst(string,subdict={}):
    for k in subdict.keys():
        string=string.replace(k,subdict[k])
    return string

if __name__ == "__main__":
    pass
    


