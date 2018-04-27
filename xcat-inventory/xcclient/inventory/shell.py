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

    @shell.arg('-t','--type', metavar='<type>', help='type of the objects to import, valid values: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, all objects in the inventory file will be imported')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='names of the objects to import, delimited with Comma(,). If not specified, all objects of the specified type in the inventory file will be imported')
    @shell.arg('-f','--path', metavar='<path>', help='path of the inventory file to import ')
    @shell.arg('-s','--schema-version',dest='version', metavar='<version>', help='schema version of the inventory file. Valid schema versions: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, the "latest" schema version will be used')
    @shell.arg('--dry', dest='dryrun', action="store_true", default=False, help='Dry run mode, nothing will be commited to xcat database')
    @shell.arg('-c','--clean', dest='update', action="store_false", default=True, help='clean mode. IF specified, all objects other than the ones to import will be removed')
    def do_import(self, args):
        """Import inventory file to xcat database"""
        mgr.validate_args(args, 'import')
        if args.type :
            #do export by type
            mgr.import_by_type(args.type, args.name, args.path, dryrun=args.dryrun,version=args.version,update=args.update)
        else :
            mgr.import_all(args.path, dryrun=args.dryrun,version=args.version,update=args.update)

    @shell.arg('-t','--type', metavar='<type>', help='type of objects to export, valid values: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, all objects EXCEPT osimage will be exported')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='names of the objects to export, delimited with Comma(,). If not specified, all objects of the specified type will be exported')
    @shell.arg('-f','--path', metavar='<path>', help='path of the inventory file(not implemented yet)')
    @shell.arg('-s','--schema-version', dest='version',metavar='<version>', help='schema version of the inventory data. Valid values: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, the "latest" schema version will be used')
    @shell.arg('--format', metavar='<format>', help='format of the inventory data, valid values: json, yaml. json will be used by default if not specified ')
    def do_export(self, args):
        """Export the inventory data from xcat database"""
        mgr.validate_args(args, 'export')
        if args.type :
            # do export by type
            mgr.export_by_type(args.type, args.name, args.path, args.format,version=args.version)
        else :
            mgr.export_all(args.path, args.format,version=args.version)

# main entry for CLI
def main():
    try:
        InventoryShell('xcat-inventory','#VERSION_SUBSTITUTE#').run(sys.argv[1:], '1.0', "xCAT inventory management tool")
    except KeyboardInterrupt:
        print("... terminating xCAT inventory management tool", file=sys.stderr)
        sys.exit(2)
    except (InvalidFileException,ObjNonExistException,CommandException,InvalidValueException,BadDBHdlException,BadSchemaException,DBException), e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    #except (ParserError), e:
    #    print("Error: invalid file!", file=sys.stderr)
    #    sys.exit(2)
    except Exception as e:
        #print(e)
        traceback.print_exc(e)
        sys.exit(1)
