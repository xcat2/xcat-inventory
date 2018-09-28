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
import utils

class Invbackend:

    defaultcfgpath="/etc/xcat/inventory.cfg"
    bkendcfg={}


    def loadcfg(self,cfgpath=None):
        if cfgpath is None:
            myhome=utils.gethome()
            cfgpath=myhome+'/.xcat/inventory.cfg' 
        if not os.path.isfile(cfgpath):
            cfgpath=self.defaultcfgpath 

        if not os.path.exists(cfgpath):
            raise InvalidFileException("The configuration file %s does not exist!\n"%(cfgpath))    

        config = configparser.ConfigParser()
        config.read(cfgpath)
        if not config:
            raise ParseException("Unable to parse configuration file %s"%(cfgpath))
        #print(config)
        self.bkendcfg['type']=config['backend']['type'].strip('"').strip("'")
        self.bkendcfg['workspace']=config['backend']['workspace'].strip('"').strip("'")
        self.bkendcfg['user']=config['backend']['user'].strip('"').strip("'")
        self.bkendcfg['InfraRepo']={}
        self.bkendcfg['InfraRepo']['remote_repo']=config['InfraRepo']['remote_repo'].strip('"').strip("'")
        self.bkendcfg['InfraRepo']['local_repo']=config['InfraRepo']['local_repo'].strip('"').strip("'")
        self.bkendcfg['InfraRepo']['working_dir']=config['InfraRepo']['working_dir'].strip('"').strip("'")


    def __initcfgfile(self):
        myhome=utils.gethome()
        cfgpath=myhome+'/.xcat/inventory.cfg'
        if not os.path.exists(cfgpath):
            if not os.path.exists(self.defaultcfgpath):
                raise FileNotExistException('File "%s" does not exist, please check ...' % self.defaultcfgpath) 
            shutil.copyfile(self.defaultcfgpath, cfgpath)   

    def init(self,cfgpath=None): 
        self.__initcfgfile()        
        self.loadcfg(cfgpath)
        if os.path.isdir(self.bkendcfg['InfraRepo']['local_repo']):
            self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
            try:
                sh.git('rev-parse','--git-dir')    
            except  sh.ErrorReturnCode as e:
                print("%s is not a git repo dir, removing..."%(self.bkendcfg['InfraRepo']['local_repo']))
                shutil.rmtree(self.bkendcfg['InfraRepo']['local_repo'])

        if not os.path.isdir(self.bkendcfg['InfraRepo']['local_repo']):
            os.mkdir(self.bkendcfg['InfraRepo']['local_repo'])
            self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])

            try:
                sh.git.clone(self.bkendcfg['InfraRepo']['remote_repo'],self.bkendcfg['InfraRepo']['local_repo'])
            except sh.ErrorReturnCode as e:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

        print("%s is a git repo dir,checking...."%(self.bkendcfg['InfraRepo']['local_repo']))
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
        if 'origin' in gitremotes.keys() and gitremotes['origin']['fetch']!=self.bkendcfg['InfraRepo']['remote_repo'] or gitremotes['origin']['push']!=self.bkendcfg['InfraRepo']['remote_repo']:
            sh.git.remote('remove','origin')
            del gitremotes['origin']
          
        if 'origin' not in gitremotes.keys():
            sh.git.remote('add','origin',self.bkendcfg['InfraRepo']['remote_repo'])

        try:
            sh.git.pull('origin','master','--tags')
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

        if self.bkendcfg['workspace'] != "master":
            sh.git.checkout('-b',self.bkendcfg['workspace'])
            sh.git.pull('origin',self.bkendcfg['workspace'],'--tags')
            
        self._change_dir(self.bkendcfg['InfraRepo']['working_dir'])
        print("xcat-inventory backend initialized",file=sys.stderr)

    def __init__(self): 
        pass
        #try:
        #    self.loadcfg()
        #    os.chdir(self.bkendcfg['InfraRepo']['local_repo'])
        #    os.chdir(self.bkendcfg['InfraRepo']['working_dir'])
        #except:
        #    raise BackendNotInitException('Backend not initialized, please initialize the backend with \'xcat-inventory init\'') 
        

    def __getstash(self):
        brstash={}
        out=sh.git.stash('list').strip()
        lines=out.split("\n")
        for line in lines:
            ment=re.findall(r'(\S+):[^:]+\s+(\S+):.+',line)
            if ment:
                if ment[0][1] not in brstash.keys():
                    brstash[ment[0][1]]=[ment[0][0]] 
                else:
                    brstash[ment[0][1]].append(ment[0][0])
        return brstash
                    
    def __getbranch(self):
        try:
            line=sh.git('symbolic-ref','-q','--short', 'HEAD')
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
        
        curworkspace=line.strip()
        return curworkspace

    def __isuncached(self):
        pass

    def __istempbranch(self,branch):
        return re.match(r'\S+@\S+',branch)

    def __iswkspacenamevalid(self,branch):
        if self.__istempbranch(branch):
            return False
        return True

    #return a list of (branch,commit) from branch name "commit@branch"
    def __parsetempbranch(self,rawbranch):
        commit=None
        branch=None
        ment=re.findall(r'(\S+)@(\S+)',rawbranch)
        if ment:
            commit=ment[0][0]
            branch=ment[0][1]
        return (branch,commit)

    def _deal_with_shErr(self, err):
        if 'fatal' in err:
            return 'Error: %s' % re.findall(r"fatal: (.+?)\n", err)[0] 
        if 'error' in err:
            errors = re.findall(r"error: (.+?)\n", err)
            err_string = ['Error: ' + error for error in errors]
            return '\n' . join(err_string)

    def _change_dir(self, target_dir):
        if not os.path.isdir(target_dir):
            raise DirNotExistException('Directory "%s" does not exist, please check...' % target_dir)
        os.chdir(target_dir)

    def workspace_list(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        try:
            lines=sh.git.branch().strip()
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
        if lines:
            rawbranches=lines.split('\n')        
            branches=[ branch.strip() for branch in rawbranches if not self.__istempbranch(branch.strip())]
            print('\n' . join(branches))
        else:
            print('No workspaces')

    def workspace_new(self,newbranch):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        if not self.__iswkspacenamevalid(newbranch):
            print("invalid workspace name: invalid character \"@\"",file=sys.stderr)
            return 1
        curbranch=self.__getbranch()
        if self.__istempbranch(curbranch):
            (branch,commit)=self.__parsetempbranch(curbranch)           
            sh.git.checkout(branch)
            sh.git.branch("-D",curbranch)
        if newbranch != curbranch:
            try:
                sh.git.checkout('-b',newbranch)
            except sh.ErrorReturnCode as e:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
        print("new workspace %s created!"%(newbranch))

    def workspace_delete(self,newbranch):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        try:
            sh.git.checkout('master')
            sh.git.branch('-D',newbranch)
            print("deleted workspace %s"%(newbranch))
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

    def workspace_checkout(self,newbranch):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        if curworkspace!=newbranch:
            sh.git.stash('save')
        if self.__istempbranch(curworkspace):
            (branch,commit)=self.__parsetempbranch(curworkspace)
            sh.git.checkout(branch)
            sh.git.branch("-D",curworkspace)
             
        try:
            sh.git.checkout(newbranch)
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

        stashdict=self.__getstash()
        if curworkspace!=newbranch and newbranch in stashdict.keys() :
            sh.git.stash('pop',stashdict[newbranch])
        print("switched to workspace %s"%(newbranch))

    #def 

    def rev_list(self,revision):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        try:
            if revision is None:
                revisions=sh.git.tag('-l').strip()
                if revisions:
                    revlist=revisions.split('\n')
    #        revlist=[rev.strip() for rev in rwrevlist if re.match(r'[^#]+#[^#]+',rev.strip()] 
                    print('\n' . join(revlist))
                else:
                    print('No revisions of the current workspace')
            else:
                revision=sh.git.show(revision)
                print(revision)
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
            

    def pull(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        print("syncing %s from remote repo"%(curworkspace))
        try:
            sh.git.pull('origin',curworkspace,'--tags')
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

    def refresh(self):
        pass
    
    def push(self, revision):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        print("push revision %s to remote repo ..."%(revision))
        try:
            sh.git.push('origin',curworkspace,'--tags')        
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

    def drop(self):
        pass
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        sh.git.reset()
        sh.git.checkout('.')
        sh.git.clean('-fdx')
        print("dropped the uncommited changes in workspace %s"%(curworkspace))
        stashdict=self.__getstash()
        while curworkspace in stashdict.keys() and stashdict[curworkspace]:
            sh.git.stash('drop',stashdict[curworkspace][0])        
            stashdict=self.__getstash()
       

    def commit(self,revision,description):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'] + '/' + self.bkendcfg['InfraRepo']['working_dir'])
        curworkspace=self.__getbranch()
        if self.__istempbranch(curworkspace):
            (branch,commit)=self.__parsetempbranch(curworkspace)
            print("you are on the %s revision of %s workspace, please run \"xcat-inventory checkout --no-import\" to switch to the head of workspace"%(commit,branch))
            return 1
        manager.export_by_type(None,None,None,'.',fmt='yaml',version=None,exclude=None)
        print("creating revision %s in workspace %s ..."%(revision,curworkspace))
        sh.git.add('./*')
        try:
            sh.git.commit('-a','-m',description)
        except sh.ErrorReturnCode as e:
            if e.stderr:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
            if e.stdout:
                raise ShErrorReturnException(' ' . join(e.stdout.split('\n')))

        if revision:
            revname="%s#%s"%(revision,curworkspace)
            sh.git.tag('-a',revname,'-m',description)
        
    def checkout(self,revision=None,doimport=True):  
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        self._change_dir(self.bkendcfg['InfraRepo']['working_dir'])
        curbranch=self.__getbranch()
        if self.__istempbranch(curbranch) :
            (branch,commit)=self.__parsetempbranch(curbranch)
            if commit == revision:
                print("already on revision %s"%(revision)) 
                return 0
            else:
                sh.git.checkout(branch)
                sh.git.branch('-D',curbranch)
                curbranch=branch
 
        revinbranch=0
        if revision is None:
            pass
        elif curbranch == revision:
            print("\"%s\" is the name of current workspace \"%s\""%(revision,curbranch))
            return 1
        else:
            try:
                lines=sh.git.branch("--contains",revision).strip()
            except sh.ErrorReturnCode as e: 
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
            if '* '+curbranch in lines:
                revinbranch=1
            if revinbranch: 
                brname=revision+'@'+curbranch 
                try:
                    sh.git.checkout('-b',brname,revision)
                except sh.ErrorReturnCode as e:
                    raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
            else:
                print("the specified \"%s\" revision cannot be found in workspace \"%s\""%(revision,curbranch))
                return 1
            
        print("checked out to revision %s"%(revision)) 
        if doimport:
            manager.importobj(None,".",None,None,None,None,False,None)

      
