###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

#
# xcat_client.py 
#
# The xCAT client API library
# It is used to run xCAT commands remotely through xCAT daemon (xcatd).
#

from .client.constants import *
from .client.timer import Timer
from .client.xcat_client_base import XCATClientBase
from .client.xcat_ssl import SSLClient

from .client.xcat_cmd_helpers import *

#
# Client library
#

class XCATClientParams(object):
    def __init__(self):
        # Hostname or IP address of SSL server
        self.host = XCAT_HOST

        # Port of SSL server
        self.port = XCAT_SSL_PORT

        # Path of file containing CA certificates to verify 
        # server certificate is signed by legitimate authority
        self.ca_certs = XCAT_SSL_CA_CERTS

        # Path of file containing client certificate and private key
        self.client_cred = XCAT_SSL_CLIENT_CRED

        # Flag to indicate if you want to use the same SSL connection
        # for multiple requests.
        self.reuse_connection = False


class XCATClientSocketOptions(object):
    def __init__(self):
        # Number of seconds to wait before retrying connection
        self.connect_timeout_sec = XCAT_CLIENT_CONNECT_TIMEOUT_SEC

        # Number of socket connection attempts before failing
        self.connect_attempts = XCAT_CLIENT_CONNECT_ATTEMPTS

        # Number of seconds to wait before retrying socket read
        self.read_timeout_sec = XCAT_CLIENT_READ_TIMEOUT_SEC

        # Number of socket read attempts before failing
        self.read_attempts = XCAT_CLIENT_READ_ATTEMPTS

        # Number of seconds to wait before retrying socket write
        self.write_timeout_sec = XCAT_CLIENT_WRITE_TIMEOUT_SEC

        # Number of socket write attempts before failing
        self.write_attempts = XCAT_CLIENT_WRITE_ATTEMPTS


class XCATClient(XCATClientBase):
    """Class used to remotely run xCAT commands through the xCAT daemon (xcatd)."""

    #
    # General operations
    #

    def init(self, logger, params=XCATClientParams(),
                           default_sockopts=XCATClientSocketOptions(),
                           cmd_sockopts={}):
        """Initialize the client object. Always call this before you call
        any client methods.
        Params: 
            logger:   Pre-created logger object
            params:   (Optional) An XCATClientParams object 
                      containing SSL connection options, like host, 
                      port, etc...
            default_sockopts: (Optional) An XCATClientSocketOptions object  
                              containing socket options, like read timeout, 
                              etc..  These options are used to run all 
                              xCAT commands by default.
            cmd_sockopts:     (Optional) A dictionary for configuring command-specific
                              socket options.  These override the default socket options.
                              e.g., cmd_sockopts = {'mkdef' : <XCATClientSocketOptions object>, 
                                                    'nodeset' : <XCATClientSocketOptions object>, 
                                                    etc...}
        """

        self._init(logger, params, default_sockopts, cmd_sockopts)
        

    def cleanup(self):
        """Cleanup the client object.  Always call this when you've finished
        using the client."""

        self._cleanup()


    #
    # Table.pm commands
    #

    def get_all_entries(self, table):
        """Returns all of the rows for a specified xCAT table
        Params:
            table: xCAT table name (str)
        Returns:
            XCATTableCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError  (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(GetAllEntriesHelper(table))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def get_nodes_attribs(self, noderange, table, attrs=[]):
        """Returns a set of attributes for a node-related xCAT table.
        Params:
            noderange: xCAT noderange expression (str)
            table: xCAT table name (str)
            attrs: xCAT table column names (list)
        Returns:
            XCATTableCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError  (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(GetNodesAttribsHelper(noderange, table, attrs))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def set_nodes_attribs(self):
        # TODO: define interface, and implement
        pass


    def del_entries(self):
        # TODO: define interface, and implement
        pass


    def set_attribs(self):
        # TODO: define interface, and implement
        pass


    def get_attribs(self):
        # TODO: define interface, and implement
        pass


    #
    # Node commands
    #

    def nodeset(self, noderange, boot_state):
        """Sets the boot state for a noderange
        Params:
            noderange: xCAT noderange expression (str)
            boot_state:  Node boot state, e.g., boot, install, etc. (str)
        Returns:
            XCATNodesetCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError  (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(NodesetHelper(noderange, boot_state))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def nodech(self, noderange, args=[]):
        """Changes nodes' attributes in the xCAT cluster database
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATNodesetCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError  (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(NodechHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def xdsh(self, noderange, args=[]):
        """Concurrently runs commands on multiple nodes
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATNodesetCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError  (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception ( 'TBI' )
            #return self._run_command(XdshHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    #
    # *def commands
    #

    def lsdef(self, args=[]):
        """List xCAT data object definitions.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(LsdefHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def mkdef(self, args=[], stdin=''):
        """Create xCAT data object definitions
        Params:
            args:      Cmd-line args (list)
            stdin:     String containing contents of a Stanza file 
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MkdefHelper(args, stdin))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def chdef(self, args=[], stdin=''):
        """Change xCAT data object definitions
        Params:
            args:      Cmd-line args (list)
            stdin:     String containing contents of a Stanza file 
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(ChdefHelper(args, stdin))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def rmdef(self, args=[]):
        """Remove xCAT data object definitions
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(RmdefHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    # make* commands

    def makedhcp(self, noderange, args=[]):
        """Generates the DHCP configuration files from info in the 
        xCAT tables.
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MakedhcpHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def makedns(self, noderange, args=[]):
        """Sets up domain name services from info in the xCAT tables.
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MakednsHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def makehosts(self, noderange, args=[]):
        """Generates the /etc/hosts from the xCAT hosts table.
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MakehostsHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def makeknownhosts(self, noderange, args=[]):
        """Generates a known_hosts file under $ROOTHOME/.ssh for the
        specified noderange.
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MakeknownhostsHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def makeconservercf(self, noderange, args=[]):
        """Generates the conserver configuration file from info in 
        in xCAT tables.
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MakeconservercfHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def mknb(self, args=[]):
        """Generates the netboot configuration file from xCAT tables.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(MknbHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    #
    # *image commands
    #

    def genimage(self, args=[]):
        """Generates a stateless image to be used for a diskless install
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(GenimageHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def packimage(self, args=[]):
        """Packs the stateless image from the chroot file system.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(PackimageHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    #
    # copycds command
    #

    def copycds(self, args=[]):
        """Copies Linux distributions and service levels from 
        CDs/DVDs to install directory
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            # return self._run_command(CopycdsHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    #
    # hardware commands
    #

    def rpower(self, noderange, args=[]):
        """Remote power control of nodes
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(RpowerHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def rvitals(self, noderange, args=[]):
        """Remote hardware vitals
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(RvitalsHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def rbeacon(self, noderange, args=[]):
        """Turns beacon on/off/blink or gives status of a node or
        noderange
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(RbeaconHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def rinv(self, noderange, args=[]):
        """Remote hardware inventory
        Params:
            noderange: xCAT noderange expression (str)
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # TODO: 
            raise Exception('TBI')
            #return self._run_command(RinvHelper(noderange, args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def discoverstart(self, args=[]):
        """Start profile node discovery.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(NodediscoverstartHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def discoverstop(self, args=[]):
        """Stop profile node discovery.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(NodediscoverstopHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def discoverls(self, args=[]):
        """List the discovered nodes.
        Params:
            args:      Cmd-line args (list)
        Returns:
            XCATGenericCmdResult  (see client/xcat_data.py)
        Exceptions:
            XCATClientError       (see client/xcat_exceptions.py)
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            return self._run_command(NodediscoverlsHelper(args))
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')
