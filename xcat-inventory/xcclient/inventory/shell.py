#!/usr/bin/env python
###############################################################################
# IBM(c) 2007 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################
# -*- coding: utf-8 -*-
#

"""
Command-line interface to xCAT inventory import/export
"""

from __future__ import print_function
from xcclient import shell
from exceptions import *
import re
import sys
import traceback
import os
import utils

try: 
    import xcclient.inventory.manager as mgr
except ImportError,e:
     if re.match(r'No module named pymysql',str(e),re.I):
         print(r'Error: '+str(e), file=sys.stderr)
         print(r"Please install package 'python-PyMySQL-0.7.x' or 'PyMySQL 0.7.x' on PyPI",file=sys.stderr)
         sys.exit(1)
     else:
         print(str(e), file=sys.stderr)
         sys.exit(1)

class InventoryShell(shell.ClusterShell):
    def add_subcommands(self, subparsers, revision):
        pass

    @shell.arg('-t','--type', metavar='<type>', help='comma "," delimited types of the objects to import, valid values: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, all objects in the inventory file will be imported')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='names of the objects to import, delimited with Comma(,). If not specified, all objects of the specified type in the inventory file will be imported')
    @shell.arg('-f','--path', metavar='<path>', help='path of the inventory file to import ')
    @shell.arg('-d','--dir', dest='directory',metavar='<directory>', help='path of the inventory directory')
    @shell.arg('-s','--schema-version',dest='version', metavar='<version>', help='schema version of the inventory file. Valid schema versions: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, the "latest" schema version will be used')
    @shell.arg('--dry', dest='dryrun', action="store_true", default=False, help='Dry run mode, nothing will be commited to xcat database')
    @shell.arg('-c','--clean', dest='update', action="store_false", default=True, help='clean mode. IF specified, all objects other than the ones to import will be removed')
    @shell.arg('-e','--env', dest='env', metavar='<env_var>', action='append', help='the values of variables in object definitions(only available for osimage object), syntax: "<variable name>=<variable value>" , this option can be used multiple times to specify multiple variables')
    def do_import(self, args):
        """Import inventory file to xcat database"""
        mgr.validate_args(args, 'import')
        mgr.importobj(args.path,args.directory,args.type,args.name,dryrun=args.dryrun,version=args.version,update=args.update,envs=args.env)

    @shell.arg('-t','--type', metavar='<type>', help='comma "," delimited types of objects to export, valid values: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, all objects in xcat databse will be exported')
    @shell.arg('-x', '--exclude', dest='exclude', default='', help='types to be excluded when exporting all, delimited with Comma(,).')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='names of the objects to export, delimited with Comma(,). If not specified, all objects of the specified type will be exported')
    @shell.arg('-f','--path', metavar='<path>', help='path of the inventory file')
    @shell.arg('-d','--dir', dest='directory',metavar='<directory>', help='path of the inventory directory')
    @shell.arg('-s','--schema-version', dest='version',metavar='<version>', help='schema version of the inventory data. Valid values: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, the "latest" schema version will be used')
    @shell.arg('--format', metavar='<format>', help='format of the inventory data, valid values: json, yaml. yaml will be used by default if not specified ')
    def do_export(self, args):
        """Export the inventory data from xcat database"""
        mgr.validate_args(args, 'export')
        mgr.export_by_type(args.type, args.name, args.path, args.directory, args.format, version=args.version, exclude=args.exclude.split(','))

    @shell.arg('--files', dest='files', metavar='FILE', nargs=2, help='compare the given 2 inventory files')
    @shell.arg('--filename', dest='filename', metavar='FILENAME', nargs=1, help='the filename want to show, be used with "--files"')
    @shell.arg('--source', dest='source', metavar='FILE', nargs=1, help='compare the given inventory file with xCAT DB')
    @shell.arg('--all', dest='all', action="store_true", default=False, help='compare the given inventory file with the whole xCAT DB, be used with "--source". If not specified, will only compare the objects in given inventory file by default.')
    def do_diff(self, args):
        """show inventory diff between files or file vs xCAT DB"""
        from inventorydiff import InventoryDiff
        InventoryDiff(args).inventory_diff()

    def do_envlist(self,args):
        """Show implicit environment variables during 'xcat-inventory import', which can be used in inventory files with format '{{<environment variable name>}}'"""
        mgr.envlist()

# main entry for CLI
def main():
    utils.initglobal()
    try:
        InventoryShell('xcat-inventory','#VERSION_SUBSTITUTE#').run(sys.argv[1:], '1.0', "xCAT inventory management tool")
    except KeyboardInterrupt:
        print("... terminating xCAT inventory management tool", file=sys.stderr)
        sys.exit(2)
    except (InvalidFileException,ObjNonExistException,CommandException,InvalidValueException,BadDBHdlException,BadSchemaException,DBException,ParseException,InternalException,ObjTypeNonExistException), e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    #except (ParserError), e:
    #    print("Error: invalid file!", file=sys.stderr)
    #    sys.exit(2)
    except Exception as e:
        #print(e)
        traceback.print_exc(e)
        sys.exit(1)
