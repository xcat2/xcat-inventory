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
import xcclient.inventory.manager as mgr

import sys
import traceback

class InventoryShell(shell.ClusterShell):
    def add_subcommands(self, subparsers, revision):
        pass

    @shell.arg('-t','--type', metavar='<type>', help='Object type to be imported, valid object types: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, import the objects of all the types in the file')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='Object names to be imported, delimited with Comma(,). If not specified, import all the objects of the specified type in the file')
    @shell.arg('-f','--path', metavar='<path>', help='File path of the inventory file to import ')
    @shell.arg('-s','--schema-version',dest='version', metavar='<version>', help='the schema version. Valid schema versions: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, use "latest" schema version')
    @shell.arg('--dry', dest='dryrun', action="store_true", default=False, help='Dry run mode, nothing will be commited to database')
    @shell.arg('-c','--clean', dest='update', action="store_false", default=True, help='clean mode, remove all the objects in xcat db before import the objects in the file. If not specified, only update existing records or insert new records, will not remove other objects in xcat db. ')
    def do_import(self, args):
        """Import the inventory based on the type or name from specified path"""
        mgr.validate_args(args, 'import')
        if args.type :
            #do export by type
            mgr.import_by_type(args.type, args.name, args.path, dryrun=args.dryrun,version=args.version,update=args.update)
        else :
            mgr.import_all(args.path, dryrun=args.dryrun,version=args.version,update=args.update)

    @shell.arg('-t','--type', metavar='<type>', help='Object type to be exported, valid object types: '+','.join(mgr.InventoryFactory.getvalidobjtypes())+'. '+'If not specified, export the inventory data of the current cluster')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='Object names to be exported, delimited with Comma(,). If not specified, export all the objects of the specified type in the file')
    @shell.arg('-f','--path', metavar='<path>', help='File path for the inventory objects to export to(not implemented yet)')
    @shell.arg('-s','--schema-version', dest='version',metavar='<version>', help='the schema version.  Valid schema versions: '+','.join(mgr.InventoryFactory.getAvailableSchemaVersions())+'. '+'If not specified, use "latest" schema version')
    @shell.arg('--format', metavar='<format>', help='The content format: json or yaml. json by default if not specified ')
    def do_export(self, args):
        """Export the inventory based on the type or name to specified path"""
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
