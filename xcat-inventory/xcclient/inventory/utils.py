#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
# common helper subroutines
#
import os
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


