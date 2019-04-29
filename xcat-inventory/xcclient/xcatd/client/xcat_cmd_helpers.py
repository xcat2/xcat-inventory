###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_cmd_helpers.py
# 
# Library containing helper classes for each xCAT command
#

from .xcat_msg import *


class GenericCmdHelper(object):
    """Helper class for generic xCAT commands"""

    def __init__(self, command='', noderange='', args=None, stdin=''):
        self.command = command
        self.noderange = noderange
        self.args = args or []
        self.stdin = stdin

    def __str__(self):
        return '%s: noderange=%s, args=%s, stdin_len=%s' % \
            (self.command, self.noderange, str(self.args), len(self.stdin))

    def get_request(self):
        return XCATRequest(command=self.command, 
                           noderange=self.noderange, 
                           args=self.args, stdin=self.stdin)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client)
        return parser.parse()


#
# Table.pm commands
#

class GetAllEntriesHelper(object):

    def __init__(self, table):
        self.command = 'getAllEntries'
        self.table = table

    def __str__(self):
        return '%s: table=%s' % (self.command, self.table)

    def get_request(self):
        return XCATRequest(command=self.command, table=self.table)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATTableCmdResultParser(req, ssl_client, row_tag='row')
        return parser.parse()


class GetNodesAttribsHelper(object):

    def __init__(self, noderange, table, attrs=None):
        self.command = 'getNodesAttribs'
        self.noderange = noderange
        self.table = table
        self.attrs = attrs or []

    def __str__(self):
        return '%s: noderange=%s, table=%s, attrs=%s' % \
            (self.command, self.noderange, self.table, str(self.attrs))

    def get_request(self):
        return XCATRequest(command=self.command,
                           noderange=self.noderange,
                           table=self.table, attrs=self.attrs)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATTableCmdResultParser(req, ssl_client, row_tag='node')
        return parser.parse()

#
# Node commands
#


class NodesetHelper(object):
    """Helper class for nodeset command"""

    def __init__(self, noderange, boot_state):
        self.command = 'nodeset'
        self.noderange = noderange
        self.boot_state = boot_state

    def __str__(self):
        return '%s: noderange=%s, boot_state=%s' % \
            (self.command, self.noderange, self.boot_state)

    def get_request(self):
        return XCATRequest(command=self.command, 
                           noderange=self.noderange, 
                           args=[self.boot_state])

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATNodesetCmdResultParser(req, ssl_client)
        return parser.parse()


class NodechHelper(GenericCmdHelper):
    """Helper class for nodech command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'nodech', noderange, args)


#
# *def commands
#

class LsdefHelper(GenericCmdHelper):
    """Helper class for lsdef command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'lsdef', args=args)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['info'])
        return parser.parse()


class MkdefHelper(GenericCmdHelper):
    """Helper class for mkdef command"""

    def __init__(self, args, stdin):
        GenericCmdHelper.__init__(self, 'mkdef', args=args, stdin=stdin)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['info'])
        return parser.parse()


class ChdefHelper(GenericCmdHelper):
    """Helper class for chdef command"""

    def __init__(self, args, stdin):
        GenericCmdHelper.__init__(self, 'chdef', args=args, stdin=stdin)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['info'])
        return parser.parse()


class RmdefHelper(GenericCmdHelper):
    """Helper class for rmdef command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'rmdef', args=args)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['info'])
        return parser.parse()

class CopycdsHelper(GenericCmdHelper):
    """Helper class for copycds command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'copycds', args=args)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['info'])
        return parser.parse()

#
# make* commands
#

class MakedhcpHelper(GenericCmdHelper):
    """Helper class for makedhcp command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'makedhcp', noderange, args)


class MakednsHelper(GenericCmdHelper):
    """Helper class for makedns command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'makedns', noderange, args)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATGenericCmdResultParser(req, ssl_client, output_msg_tags=['contents', 'info'])
        return parser.parse()


class MakehostsHelper(GenericCmdHelper):
    """Helper class for makehosts command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'makehosts', noderange, args)


class MakeknownhostsHelper(GenericCmdHelper):
    """Helper class for makeknownhosts command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'makeknownhosts', noderange, args)


class MakeconservercfHelper(GenericCmdHelper):
    """Helper class for makeconservercf command"""

    def __init__(self, noderange, args):
        GenericCmdHelper.__init__(self, 'makeconservercf', noderange, args)


class MknbHelper(GenericCmdHelper):
    """Helper class for mknb command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'mknb', args=args)


class NodediscoverstartHelper(GenericCmdHelper):
    """Helper class for mknb command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'nodediscoverstart', args=args)


class NodediscoverstopHelper(GenericCmdHelper):
    """Helper class for mknb command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'nodediscoverstop', args=args)


class NodediscoverlsHelper(GenericCmdHelper):
    """Helper class for mknb command"""

    def __init__(self, args):
        GenericCmdHelper.__init__(self, 'nodediscoverls', args=args)

    def parse_response(self, ssl_client):
        req = self.get_request()
        parser = XCATTableCmdResultParser(req, ssl_client, row_tag='node')
        return parser.parse()
