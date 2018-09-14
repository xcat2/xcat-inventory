#!/usr/bin/python
from __future__ import print_function
import 	configparser
import os
import sh
import shutil
import re
import sys
from exceptions import * 
import manager 

class Invbackend:

    invcfgpath="/etc/xcat/inventory.cfg"
    bkendcfg={}


    def loadcfg(self,cfgpath=invcfgpath):
        if not os.path.exists(cfgpath):
            raise InvalidFileException("The configuration file %s does not exist!\n"%(cfgpath))    
        config = configparser.ConfigParser()
        config.read(cfgpath)
        if not config:
            raise ParseException("Unable to parse configuration file %s"%(cfgpath))
        self.bkendcfg['type']=config['backend']['type']
        self.bkendcfg['remoteurl']=config['backend']['remote_repo'].strip('"').strip("'")
        self.bkendcfg['localpath']=config['backend']['local_repo'].strip('"').strip("'")
        self.bkendcfg['workspace']=config['backend']['workspace'].strip('"').strip("'")
        self.bkendcfg['user']=config['backend']['user'].strip('"').strip("'")

    def init(self,cfgpath=invcfgpath): 
        self.loadcfg(cfgpath)
        if os.path.isdir(self.bkendcfg['localpath']):
            os.chdir(self.bkendcfg['localpath'])
            try:
                sh.git('rev-parse','--git-dir')    
            except  sh.ErrorReturnCode as e:
                print("%s is not a git repo dir, removing..."%(self.bkendcfg['localpath']))
                shutil.rmtree(self.bkendcfg['localpath'])

        if not os.path.isdir(self.bkendcfg['localpath']):
            #import pdb
            #pdb.set_trace()
            os.mkdir(self.bkendcfg['localpath'])
            os.chdir(self.bkendcfg['localpath'])
            sh.git.clone(self.bkendcfg['remoteurl'],self.bkendcfg['localpath'])


        print("%s is a git repo dir,checking...."%(self.bkendcfg['localpath']))
        sh.git.config('--global','diff.tool','invdiff')
        sh.git.config('--global','difftool.invdiff.cmd','xcat-inventory diff --filename $MERGED --files $LOCAL $REMOTE')
        output=sh.git.remote('-v')
        gitremotes={}
        for line in output.split("\n"):
            matches=re.findall(r'^(\S+)\s+(\S+)\s+\((\S+)\)$',line)
            if matches:
                if matches[0][0] not in gitremotes.keys():
                    gitremotes[matches[0][0]]={}
                gitremotes[matches[0][0]].update({matches[0][2]:matches[0][1]})
        if 'origin' in gitremotes.keys() and gitremotes['origin']['fetch']!=self.bkendcfg['remoteurl'] or gitremotes['origin']['push']!=self.bkendcfg['remoteurl']:
            sh.git.remote('remove','origin')
            del gitremotes['origin']
          
        if 'origin' not in gitremotes.keys():
            sh.git.remote('add','origin',self.bkendcfg['remoteurl'])

        sh.git.pull('origin','master','--tags')
        if self.bkendcfg['workspace'] != "master":
            sh.git.checkout('-b',self.bkendcfg['workspace'])
            sh.git.pull('origin',self.bkendcfg['workspace'],'--tags')
    
        print("xcat-inventory backend initialized",file=sys.stderr)

    def __init__(self,cfgpath=invcfgpath): 
        self.loadcfg(cfgpath)
        #os.chdir(self.bkendcfg['localpath'])
         

    def workspace_list(self):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        lines=sh.git.branch()
        branches=lines.split('\n')        
        print(branches)

    def workspace_new(self,newbranch):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        sh.git.checkout('-b',newbranch)


    def workspace_delete(self,newbranch):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        sh.git.checkout('master')
        sh.git.branch('-D',newbranch)

    def workspace_checkout(self,newbranch):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        sh.git.checkout(newbranch)
        print("switched to workspace %s"%(newbranch))

    def rev_list(self,revision):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        if revision is None:
            revisions=sh.git.tag('-l')
            revlist=revisions.split('\n')
            print(revlist)
        else:
            revision=sh.git.show(revision)
            print(revision)
            
    def checkout(self,revision):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        print(sh.git.checkout(revision))
        print("checked out to revision %s"%(revision)) 

    def sync(self):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        line=sh.git('symbolic-ref','-q','--short', 'HEAD') 
        curworkspace=line.strip()
        print("syncing %s from remote repo"%(curworkspace))
        sh.git.pull('origin',curworkspace,'--tags')

    def refresh(self):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])   
        manager.export_by_type(None,None,None,'.',fmt='yaml',version=None,exclude=None)
    
    def push(self,revision,description):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        line=sh.git('symbolic-ref','-q','--short', 'HEAD')
        curworkspace=line.strip()
        print("creating revision %s in workspace %s ..."%(revision,curworkspace))
        sh.git.add('./*')
        sh.git.commit('-a','-m',description)
        sh.git.tag('-a',revision,'-m',description)
        print("push revision %s to remote repo ..."%(revision))
        sh.git.push('origin',curworkspace,'--tags')        

    def drop(self):
        self.loadcfg()
        os.chdir(self.bkendcfg['localpath'])
        line=sh.git('symbolic-ref','-q','--short', 'HEAD')
        curworkspace=line.strip() 
        sh.git.reset()
        sh.git.checkout('-','.')
        sh.git.clean('-fdx')
        print("dropped the uncommited changes in workspace %s"%(curworkspace))
