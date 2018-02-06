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

    @shell.arg('-t','--type', metavar='<type>', help='Object type to be imported')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='Object names to be imported')
    @shell.arg('-f','--path', metavar='<path>', help='File path for the inventory objects to import from ')
    @shell.arg('-s','--schema-version',dest='version', metavar='<version>', help='the schema version ')
    @shell.arg('--dry', dest='dryrun', action="store_true", default=False, help='Dry run mode, nothing will be commited to database')
    def do_import(self, args):
        """Import the inventory based on the type or name from specified path"""
        mgr.validate_args(args, 'import')
        if args.type :
            #do export by type
            mgr.import_by_type(args.type, args.name, args.path, dryrun=args.dryrun,version=args.version)
        else :
            mgr.import_all(args.path, dryrun=args.dryrun,version=args.version)

    @shell.arg('-t','--type', metavar='<type>', help='Object type to be exported')
    @shell.arg('-o','--objects', dest='name',metavar='<name>', help='Object names to be exported')
    @shell.arg('-f','--path', metavar='<path>', help='File path for the inventory objects to export to(not implemented yet)')
    @shell.arg('-s','--schema-version', dest='version',metavar='<version>', help='the schema version ')
    @shell.arg('--format', metavar='<format>', help='The content format: json or yaml')
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
        InventoryShell('xcat-inventory').run(sys.argv[1:], '1.0', "xCAT inventory management tool")
    except KeyboardInterrupt:
        print("... terminating xCAT inventory management tool", file=sys.stderr)
        sys.exit(2)
    except (InvalidFileException,ObjNonExistException,CommandException,InvalidValueException,BadDBHdlException,BadSchemaException), e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    #except (ParserError), e:
    #    print("Error: invalid file!", file=sys.stderr)
    #    sys.exit(2)
    except Exception as e:
        #print(e)
        traceback.print_exc(e)
        sys.exit(1)
