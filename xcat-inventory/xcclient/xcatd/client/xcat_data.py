###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_data.py 
#
# Classes for storing xCAT request and response data
#

#
# Classes for storing xCAT request data
#


class XCATRequest(object):
    """Stores data for an xCAT command request."""
    def __init__(self, command='', noderange='', args=None,
                 cwd='/tmp', clienttype='cli', table='', attrs=None, stdin='', env_vars=None):
        self.command = command
        self.noderange = noderange
        self.args = args or []
        self.cwd = cwd
        self.clienttype = clienttype
        self.table = table
        self.attrs = attrs or []
        self.stdin = stdin
        self.env_vars = env_vars or {}

    def __str__(self):
        return 'req: command=%s, noderange=%s, args=%s, cwd=%s, clienttype=%s, ' \
               'table=%s, attrs=%s, stdin_len=%s env_vars_len=%s' % \
            (str(self.command), str(self.noderange), str(self.args), 
             str(self.cwd), str(self.clienttype), str(self.table), 
             str(self.attrs), len(self.stdin), len(self.env_vars))

#
# Classes for storing xCAT response data
#


class XCATNodesetRecord(object):
    """Stores one node record returned by xCAT nodeset command"""

    def __init__(self, name='', imgserver='', data='', destiny='',
                 error='', errorcode=''):
        self.name = name
        self.imgserver = imgserver
        self.data = data
        self.destiny = destiny
        self.error = error
        self.errorcode = errorcode

    def __str__(self):
        return 'nodeset: name=%s, imgserver=%s, data=%s, destiny=%s, error=%s, errorcode=%s' % \
               (str(self.name), str(self.imgserver), str(self.data),
                str(self.destiny), str(self.error), str(self.errorcode))

    def __eq__(self, other):
        return self.name == other.name and \
               self.imgserver == other.imgserver and \
               self.data == other.data and self.destiny == other.destiny and \
               self.error == other.error and self.errorcode == other.errorcode


class XCATErrorRecord(object):
    """Stores error info returned by an xCAT command"""

    def __init__(self, error='', errorcode=''):
        self.error = error
        self.errorcode = errorcode

    def __str__(self):
        return 'Error: error=%s, errorcode=%s' % (str(self.error), str(self.errorcode))

    def __eq__(self, other):
        return self.error == other.error and self.errorcode == other.errorcode

#
# Classes to store results for different xCAT commands
#


class XCATGenericCmdResult(object):
    """Stores the basic result for an xCAT command."""

    def __init__(self):
        # Store original request info here (XCATRequest)
        self.req = None

        # Store output messages returned by the command here as
        # list of strings
        self.output_msgs = []

        # If command fails, store all errors here as list of XCATErrorRecord
        # objects
        self.errors = []

    def succeeded(self):
        return len(self.errors) == 0

    def failed(self):
        return len(self.errors) > 0

    def has_output_msgs(self):
        return len(self.output_msgs) > 0

    def get_merged_output_msgs(self):
        """Merge all output msgs into one string"""
        return '\n'.join([m for m in self.output_msgs])

    def get_error_msg(self, raw=True):
        """Generate an error message for xCAT command failure"""
        error_msg = ''
        if len(self.errors) == 1:
            error = self.errors[0]
            error_msg = str(error.error).rstrip()
            if not raw:
                error_msg = 'Failed to run %s due to: %s (code=%s)' % \
                            (self.req.command, error_msg, error.errorcode)
        elif len(self.errors) > 1:
            # Multiple errors occurred.  Just combine all of them into
            # one message.
            if raw:
                error_msg = ''
                for error in self.errors:
                    error_msg += '%s\n' % str(error.error).rstrip()
            else:
                error_msg = 'Failed to run %s due to: multiple errors.\n' % \
                            self.req.command
                for error in self.errors:
                    error_msg += 'Error: %s (code=%s)\n' % (str(error.error).rstrip(), error.errorcode)

        return error_msg


class XCATTableCmdResult(XCATGenericCmdResult):
    """Stores results of an xCAT table command."""

    def __init__(self):
        XCATGenericCmdResult.__init__(self)

        # Name of table operated on by table command
        self.table = ''

        # List of XCATTableRow objects
        self.rows = []

    def __str__(self):
        return 'table_result: table=%s, rows=%s' % \
               (str(self.table), len(self.rows))


class XCATNodesetCmdResult(XCATGenericCmdResult):
    """Stores results of xCAT nodeset command."""

    def __init__(self):
        XCATGenericCmdResult.__init__(self)

        # Dictionary of XCATNodesetRecord objects
        # Key = nodename
        self.node_dict = {}

        # List of nodenames for which nodeset command succeeded
        self.success_nodes = []

        # List of nodenames for which nodeset command failed
        self.failed_nodes = []

    def succeeded(self):
        return len(self.errors) == 0 and len(self.failed_nodes) == 0

    def failed(self):
        return len(self.errors) > 0 or len(self.failed_nodes) > 0

    def get_error_msg(self):
        """Generate an error message for nodeset command failure"""
        error_msg = XCATGenericCmdResult.get_error_msg(self)
        if error_msg:
            return error_msg

        if len(self.failed_nodes) == 1:
            # One node failed
            failed_node = self.failed_nodes[0]
            error = self.node_dict[failed_node].error
            errorcode = self.node_dict[failed_node].errorcode
            error_msg = 'Failed to run %s on %s due to: %s (code=%s)' % \
                        (self.req.command, failed_node, str(error).rstrip(), errorcode)

        elif len(self.failed_nodes) > 1:
            # Multiple nodes failed
            num_nodes = len(self.failed_nodes)
            unique_errors = \
                set([self.node_dict[n].error for n in self.failed_nodes])

            if len(unique_errors) == 1:
                error = self.node_dict.values()[0].error
                errorcode = self.node_dict.values()[0].errorcode
                error_msg = 'Failed to run %s on %s nodes due to: %s (code=%s)' % \
                            (self.req.command, num_nodes, str(error).rstrip(), errorcode)
            else:
                error_msg = 'Failed to run %s on %s nodes due to: multiple errors' % \
                            (self.req.command, num_nodes)

        return error_msg

    def __str__(self):
        return 'nodeset_result: success_nodes=%s, failed_nodes=%s' % \
               (len(self.success_nodes), len(self.failed_nodes))

#
# Classes to store primitive data
#


class XCATTableRow(dict):
    """Stores one table row of data returned by xCAT table command, like 
    getAllEntries. 

    This class works like a Python dictionary, but also gives you the 
    ability to access the dictionary key/values as regular attributes.

        e.g., r = XCATRecord()
              r['node'] = 'compute0'
              print r.node   =>   'compute0'
    """

    def __init__(self):
        dict.__init__(self)

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

    def __str__(self):
        return dict.__str__(self)

    def __eq__(self, other):
        return dict.__eq__(self, other)
