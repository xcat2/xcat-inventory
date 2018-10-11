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

    globalcfgpath="/etc/xcat/inventory.cfg"
    bkendcfg={}


    def loadcfg(self,cfgpath=None):
        if cfgpath is None:
            myhome=utils.gethome()
            cfgpath=myhome+'/.xcat/inventory.cfg' 
        if not os.path.isfile(cfgpath):
            cfgpath=self.globalcfgpath 

        if not os.path.exists(cfgpath):
            raise InvalidFileException("The configuration file %s does not exist!\n"%(cfgpath))    

        config = configparser.ConfigParser()
        config.read(cfgpath)
        if not config:
            raise ParseException("Unable to parse configuration file %s"%(cfgpath))
        #print(config)
        if 'type' in config['backend'].keys():
            self.bkendcfg['type']=config['backend']['type'].strip('"').strip("'")

        if 'workspace' in config['backend'].keys():
            self.bkendcfg['workspace']=config['backend']['workspace'].strip('"').strip("'")

        if 'user' in config['backend'].keys():
            self.bkendcfg['user']=config['backend']['user'].strip('"').strip("'")

        if 'email' in config['backend'].keys():
            self.bkendcfg['email']=config['backend']['email'].strip('"').strip("'")

        self.bkendcfg['InfraRepo']={}
        if 'remote_repo' in config['InfraRepo'].keys(): 
            self.bkendcfg['InfraRepo']['remote_repo']=config['InfraRepo']['remote_repo'].strip('"').strip("'")

        if 'local_repo' in config['InfraRepo'].keys(): 
            self.bkendcfg['InfraRepo']['local_repo']=config['InfraRepo']['local_repo'].strip('"').strip("'")

        if 'working_dir' in config['InfraRepo'].keys(): 
            self.bkendcfg['InfraRepo']['working_dir']=config['InfraRepo']['working_dir'].strip('"').strip("'")
        else:
            self.bkendcfg['InfraRepo']['working_dir']='.'
         


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
            os.makedirs(self.bkendcfg['InfraRepo']['local_repo'])
            self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
            print("cloning remote repo %s to %s ..."%(self.bkendcfg['InfraRepo']['remote_repo'],self.bkendcfg['InfraRepo']['local_repo']))
            try:
                sh.git.clone(self.bkendcfg['InfraRepo']['remote_repo'],self.bkendcfg['InfraRepo']['local_repo'])
            except sh.ErrorReturnCode as e:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

        print("%s is a git repo dir,configuring...."%(self.bkendcfg['InfraRepo']['local_repo']))
        sh.git.config('--local','user.name',self.bkendcfg['user'])
        sh.git.config('--local','user.email',self.bkendcfg['email'])
        sh.git.config('--local','diff.tool','invdiff')
        sh.git.config('--local','difftool.invdiff.cmd','xcat-inventory diff --filename $MERGED --files $LOCAL $REMOTE')
        output=sh.git.remote('-v',_tty_out=False)
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

        if self.bkendcfg['InfraRepo']['working_dir'] and self.bkendcfg['InfraRepo']['working_dir']!='.':
            os.makedirs(self.bkendcfg['InfraRepo']['working_dir'])
        #try:
        #    sh.git.pull('origin','master','--tags')
        #except sh.ErrorReturnCode as e:
        #    raise ShErrorReturnException(self._deal_with_shErr(e.stderr))


        if self.bkendcfg['workspace']:
            print("creating workspace %s ..."%(self.bkendcfg['workspace']))
            try:
                sh.git.checkout('-b',self.bkendcfg['workspace'])
                if self.bkendcfg['InfraRepo']['working_dir']:            
                    self._change_dir(self.bkendcfg['InfraRepo']['working_dir'])
                sh.git.pull('origin',self.bkendcfg['workspace'],'--tags')
            except sh.ErrorReturnCode as e:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))


        print("xcat-inventory backend initialized")

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
        out=sh.git.stash('list',_tty_out=False).strip()
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
        return self._validatebrname(branch)

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
        if not target_dir:
            return
        if not os.path.isdir(target_dir):
            raise DirNotExistException('Directory "%s" does not exist, please check...' % target_dir)
        os.chdir(target_dir)

    def _validatebrname(self,brname):
        if brname and re.match(r'[^@^#]*(@|#)[^@^#]*',brname):
            return False
        else:
           return True
    

    def workspace_list(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        try:
            lines=sh.git.branch(_tty_out=False).strip()
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
            raise InvalidValueException("invalid character \"@\" or \"#\" found in workspace name %s"%(newbranch))
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
        print("workspace %s created!"%(newbranch))

    def workspace_delete(self,branch):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        if not self.__iswkspacenamevalid(branch):
            raise InvalidValueException("invalid character \"@\" or \"#\" found in workspace name %s"%(branch))
            return 1
        try:
            revlist=self.__getallrev(branch)
            if revlist:
                revlist=["%s#%s"%(rev,branch) for rev in revlist]
                sh.git.tag('-d',' '.join(revlist))
            sh.git.checkout('master')
            sh.git.branch('-D',branch)
            print("deleted workspace %s"%(branch))
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

    def workspace_checkout(self,newbranch):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        if not self.__iswkspacenamevalid(newbranch):
            raise InvalidValueException("invalid character \"@\" or \"#\" found in workspace name %s"%(newbranch))
            return 1
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

        while True:
            stashdict=self.__getstash()
            if curworkspace!=newbranch and newbranch in stashdict.keys() :
                stashlist=stashdict[newbranch]
                sh.git.stash('pop',stashlist[0])
            else:
                break

        self.checkout(revision=None,doimport=True)
        print("switched to workspace %s"%(newbranch))


    def __tag2rev(self,branch,tagname):
        itemmatched=re.findall(r'^([^#]+)#%s$'%(branch),tagname)
        if itemmatched:
            return itemmatched[0]       
        else:
            None  

    def __getallrev(self,branch):
        tags=sh.git.tag('-l',_tty_out=False).strip()
        if tags:
            rawtaglist=tags.split('\n') 
            revlist=[]
            for rev in rawtaglist:
                myrev=self.__tag2rev(branch,rev)
                if myrev is not None:
                    revlist.append(myrev)
            return revlist
        return None

    def __getcurrev(self,branch):
         try:
             rawtag=sh.git.describe('--candidates','0').strip()
         except:
             return None
         rev=self.__tag2rev(branch,rawtag)
         return rev

         
      

    def rev_list(self,revision):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        if self.__istempbranch(curworkspace):
            (branch,commit)=self.__parsetempbranch(curworkspace)
            curworkspace=branch
        try:
            if revision is None:
                    revlist=self.__getallrev(curworkspace)
                    if revlist:
                        print('\n' . join(revlist))
                    else:
                        print('No revision found in current workspace')
            else:
                if not self._validatebrname(revision):
                    raise InvalidValueException("invalid character \"@\" or \"#\" found in revision name %s"%(revision))
                    return 1
                revision=sh.git.show("%s#%s"%(revision,curworkspace),_tty_out=False)
                print(revision)
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
       
    def diff(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'] + '/' + self.bkendcfg['InfraRepo']['working_dir'])
        curworkspace=self.__getbranch()
        try:
            sh.git.stash('save','--all')
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
        
        print("exporting inventory data from xCAT DB...")
        devNull = open(os.devnull, 'w')
        with utils.stdout_redirector(devNull),utils.stderr_redirector(devNull):
            manager.export_by_type(None,None,None,'.',fmt='yaml',version=None,exclude=None)
        print("generating diff report...") 
        sh.git.add("./*")
        diffout=sh.git.difftool('--cached','-y',_tty_out=False,_tty_in=True) 
        print(diffout)
        sh.git.reset("--hard")

        while True:
            stashdict=self.__getstash()
            if curworkspace in stashdict.keys() :
                stashlist=stashdict[curworkspace]
                sh.git.stash('pop',stashlist[0])
            else:
                break
        

    def pull(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        if self.__istempbranch(curworkspace):
            (branch,commit)=self.__parsetempbranch(curworkspace)
            raise InvalidValueException("you are on the %s revision of %s workspace, cannot sync with remote repo"%(commit,branch))
            return 1
        print("syncing workspace %s from remote repo"%(curworkspace))
        try:
            sh.git.pull('origin',curworkspace,'--tags')
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))

    def refresh(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        try:
            sh.git.stash('save','--include-untracked')
            stashdict=self.__getstash()
            while curworkspace in stashdict.keys() and stashdict[curworkspace]:
                sh.git.stash('drop',stashdict[curworkspace][0])        
                stashdict=self.__getstash()
        except sh.ErrorReturnCode as e:
            raise ShErrorReturnException(self._deal_with_shErr(e.stderr))                
    
    def push(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        curworkspace=self.__getbranch()
        if self.__istempbranch(curworkspace):
            (branch,commit)=self.__parsetempbranch(curworkspace)
            raise InvalidValueException("you are on the %s revision of %s workspace, cannot sync with remote repo"%(commit,branch))
            return 1
        print("pushing workspace %s to remote repo ..."%(curworkspace))
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
            raise InvalidValueException("you are on the %s revision of %s workspace, please run \"xcat-inventory checkout --no-import\" to switch to the head of workspace"%(commit,branch))
            return 1

        if not self._validatebrname(revision):
            raise InvalidValueException("invalid character \"@\" or \"#\" found in revision name %s"%(revision))
            return 1
        print("exporting inventory data from xCAT DB....")
        devNull = open(os.devnull, 'w')
        with utils.stdout_redirector(devNull),utils.stderr_redirector(devNull):
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
    
    def whereami(self):
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])    
        curbranch=self.__getbranch()
        if self.__istempbranch(curbranch) :
            (branch,commit)=self.__parsetempbranch(curbranch)
        else:
            branch=curbranch
            commit=self.__getcurrev(branch)
        if commit:
            print("you are in revision \"%s\" of workspace \"%s\""%(commit,branch)) 
        else:
            print("you are in workspace \"%s\""%(branch))

    def checkout(self,revision=None,doimport=True):  
        self.loadcfg()
        self._change_dir(self.bkendcfg['InfraRepo']['local_repo'])
        self._change_dir(self.bkendcfg['InfraRepo']['working_dir'])
        curbranch=self.__getbranch()
        
        if not self._validatebrname(revision):
            raise InvalidValueException("invalid character \"@\" or \"#\" found in revision name %s"%(revision))
            return 1

        if self.__istempbranch(curbranch) :
            (branch,commit)=self.__parsetempbranch(curbranch)
            if commit == revision:
                print("already on revision %s"%(revision)) 
                return 0
            else:
                sh.git.checkout(branch)
                sh.git.branch('-D',curbranch)
                curbranch=branch


        revlist=self.__getallrev(curbranch)
        if revision:
            if not revlist or revision not in revlist:
                raise InvalidValueException("revision %s not found in workspace %s"%(revision,curbranch))
                return 1
 
        if revision is None:
            pass
        else:
            brname=revision+'@'+curbranch 
            try:
                sh.git.checkout('-b',brname,"%s#%s"%(revision,curbranch))
            except sh.ErrorReturnCode as e:
                raise ShErrorReturnException(self._deal_with_shErr(e.stderr))
            #else:
            #    print("the specified \"%s\" revision cannot be found in workspace \"%s\""%(revision,curbranch))
            #    return 1
            
        print("importing inventory data to xCAT DB...")
        if doimport:
            devNull = open(os.devnull, 'w')
            with utils.stdout_redirector(devNull),utils.stderr_redirector(devNull):
                manager.importobj(None,".",None,None,None,None,False,None)

        print("checked out to revision %s"%(revision)) 
      
