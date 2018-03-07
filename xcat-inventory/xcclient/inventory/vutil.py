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
    ValidIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"; 
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


if __name__ == "__main__":
    pass
    #expression='x: isRegex(x)'
    #f=eval("lambda "+expression)
    #print (f(sys.argv[1]))
    


