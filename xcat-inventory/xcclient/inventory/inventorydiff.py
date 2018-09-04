#!/usr/bin/env python

from __future__ import print_function
from structurediff import StructureDiff
import manager as mgr 
from exceptions import *
from utils import *
import re

def line_diff(file1, file2):
    (retcode,out,err)=runCommand("diff -u %s %s"%(file1, file2))
    if out:
        out=re.sub(r"%s.*"%(file1),file2,out)
        out=re.sub(r"%s.*"%(file2),file2,out)
    if err:
        err=re.sub(r"%s.*"%(file1),file2,err)
        err=re.sub(r"%s.*"%(file2),file2,err)
    return out, err


class InventoryDiff(object):
    def __init__(self, args, check=False):
        if check:
            self._validate_args(args)

    def _validate_args(self, args):
        if args.files and args.source:
            raise CommandException("Error: '--files' and '--source' cannot be used together!")
        if not args.files and not args.source:
            raise CommandException("Error: No valid source type!")
        if not args.source and args.all:
            raise CommandException("Error: '--all' must be used with '--source'!")
        if not args.files and args.fn:
            raise CommandException("Error: '--fn' must be used with '--files'!")

        if args.files:
            self.objs = args.files
            self.objtype = 'f'
            self.filename = args.fn
        elif args.source:
            self.objs = args.source
            self.objtype = 'fvso'
        self.isall = args.all

    def _get_file_data(self, data_file):
        data, self.fmt = loadfile(filename=data_file)
        return data

    def show_diff(self, diff, source=None):
        print("\n====================BEGIN=====================\n")
        if source:
            print(source)
        print(diff)
        print("\n====================END=====================\n")

    def inventory_diff(self):
        rc = None
        err = None
        if self.objtype == 'f':
            file1 = self.objs.pop(0)
            file2 = self.objs.pop(0)
            try:
                d1 = self._get_file_data(file1)
                d2 = self._get_file_data(file2)
            except FileNotExistException as e:
                err = e.message
                rc = 1
            except InvalidFileException as e:
                out, err = line_diff(file1, file2)
                rc = 1
            if self.filename:
                file1 = self.filename
                file2 = self.filename
        elif self.objtype == 'fvso':
            file1 = 'xCAT DB'
            file2 = self.objs.pop(0)
            try:
                d2 = self._get_file_data(file2)
                if type(d2) != dict:
                    err = 'Error: Format of data from file \'%s\' is not correct, please check...' % file2
                    rc = 1
            except FileNotExistException as e:
                err = e.message
                rc = 1
            except InvalidFileException as e:
                err = 'Error: Could not get json or yaml data from file \'%s\', please check or export object to diff files' % file2
                rc = 1
            if not rc:
                d1 = mgr.export_by_type(None, None, fmt='dict')

        if rc and err:
            return print(err)

        if not rc:
            diff_dict = StructureDiff().diff(d1, d2, self.isall)
            self.show_diff(StructureDiff().repet(diff_dict, self.fmt), "\n--- %s\n+++ %s" % (file1, file2))
        elif out:
            self.show_diff(out)

